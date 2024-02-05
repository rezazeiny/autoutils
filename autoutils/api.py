import dataclasses
import json
import logging
import time
from typing import Optional, Union, List, Dict

from requests import Session, Response

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class ServerResponse:
    """
        Server response
    """
    response: "Response" = None
    status_code: int = 503

    def __post_init__(self):
        if self.response is not None:
            self.status_code = self.response.status_code

    @property
    def json_response(self) -> Optional[Union[List, Dict]]:
        if not self.response:
            return None
        try:
            return self.response.json()
        except json.JSONDecodeError:
            pass


@dataclasses.dataclass
class BaseApi:
    name: str
    base_url: str
    token: str
    connection_timeout: int = 60
    validate_cert: bool = True
    user_agent: str = "autoutils"
    retry_count: int = 1
    retry_delay: int = 3
    token_name: str = "Bearer"
    supported_http_methods: List[str] = None

    def __post_init__(self):
        if not self.supported_http_methods:
            self.supported_http_methods = ["GET", "PUT", "DELETE", "POST", "PATCH"]
        self.session = Session()

    def _send(self, method: str, path: str, content: dict = None, files=None,
              query_params: dict = None, is_json=True):
        method = method.upper()
        if method not in self.supported_http_methods:
            raise Exception(f"Unsupported HTTP method: {method}")
        if query_params is None:
            query_params = {}
        headers = {
            "User-Agent": self.user_agent,
            "Authorization": f"{self.token_name} {self.token}"
        }
        endpoint = self.base_url + path
        logger.info(f"{self.name} api: method {method} with url {endpoint} start")
        if is_json:
            send_data = {
                "json": content
            }
        else:
            send_data = {
                "data": content,
                "files": files
            }
        retry_count = 0
        while retry_count < self.retry_count:
            try:
                response = self.session.request(
                    method, endpoint,
                    params=query_params,
                    headers=headers,
                    verify=self.validate_cert,
                    timeout=self.connection_timeout,
                    **send_data
                )
                logger.info(
                    f"{self.name} api: method {method} with url {endpoint} end. status code {response.status_code}")
                return ServerResponse(response=response)
            except Exception as e:
                logger.error(f"{self.name} api: method {method} with url {endpoint} has error {e}")
            retry_count += 1
            if retry_count < self.retry_count:
                logger.error(f"{self.name} api: method {method} with url {endpoint} wait {self.retry_delay}")
                time.sleep(self.retry_delay)
        return ServerResponse()
