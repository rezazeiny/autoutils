import json

from requests import Session


class BaseApi:
    """
        Use this class for handle all api
        Attributes:
            base_url (str) : base url
            token (str) : request token
            default_429_wait_time (int) : if response code is 429 wait this time
            connection_timeout (int) : wait this time for connect
            validate_cert (bool) : validate certificate for https connection
            user_agent (str) : default user agent for connection
            retry_count (int) : default retry count when error acquire
            retry_delay (int) : time to wait in error condition for next try
    """

    def __init__(self, base_url: str, token: str = None, default_429_wait_time: int = 5,
                 connection_timeout: int = 60, validate_cert: bool = True, user_agent: str = None,
                 retry_count: int = 1, retry_delay: int = 3):
        self.base_url = base_url
        self.token = token
        self.validate_cert = validate_cert
        self.session = Session()
        self.default_429_wait_time = default_429_wait_time
        self.connection_timeout = connection_timeout
        self.user_agent = user_agent
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    def _send(self, method: str, path:str, api_path: str = "", content:dict=None, query_params:dict=None, headers=None, return_json=True):
        """
            Same function for send api request
        Args:
            method (str):
            path (str):
            api_path:
            content:
            query_params:
            headers:
            return_json:

        Returns:

        """
        if query_params is None:
            query_params = {}
        if headers is None:
            headers = {}

        if "User-Agent" not in headers and self.user_agent:
            headers["User-Agent"] = self.user_agent

        method = method.upper()
        if method not in ["GET", "PUT", "DELETE", "POST", "PATCH"]:
            raise Exception(f"Unsupported HTTP method: {method}")

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        query_params["access_token"] = self.token

        endpoint = self.base_url + api_path + path

        if headers["Content-Type"] == "application/json" and content is not None:
            content = json.dumps(content)
        while True:
            try:
                response = self.session.request(
                    method, endpoint,
                    params=query_params,
                    data=content,
                    headers=headers,
                    verify=self.validate_cert,
                    timeout=self.connection_timeout,
                )
            except RequestException as e:
                raise MatrixHttpLibError(e, method, endpoint)
            try:
                json_response = response.json()
            except Exception as e:
                logger.error(e)
                json_response = {}
            if response.status_code == codes.too_many_requests:
                wait_time = json_response.get('retry_after_ms', self.default_429_wait_ms / 1000)
                if json_response.get('error') is not None:
                    logger.error(json_response.get('error'))
                sleep(wait_time)
            else:
                break

        if response.status_code < codes.ok or response.status_code >= codes.multiple_choices:
            raise MatrixRequestError(
                code=response.status_code, content=response.text
            )
        if return_json:
            return json_response
        else:
            return response
