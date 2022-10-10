"""
Matrix Client
"""
import logging

from .api import MatrixHttpApi
from .errors import MatrixRequestError, MatrixUnexpectedResponse
from .room import Room

logger = logging.getLogger(__name__)


class MatrixClient(object):
    """
    The client API for Matrix. For the raw HTTP calls, see MatrixHttpApi.

    Args:
        token (Optional[str]): If you have an access token
            supply it here.
        valid_cert_check (bool): Check the home servers
            certificate on connections?
    Returns:
        `MatrixClient`
    Raises:
        `MatrixRequestError`, `ValueError`
    Examples:
        Create a new user and send a message::
            client = MatrixClient()
            token = client.login(username="foobar",
                password="monkey")
            room = client.create_room("my_room")
            room.send_image(file_like_object)
    """

    def __init__(self, base_url: str, *, token: str = None,
                 valid_cert_check: bool = True, sync_filter_limit: int = 20,
                 api_connection_timeout: int = 60, device_id: str = None):

        self.api = MatrixHttpApi(base_url=base_url, token=token,
                                 connection_timeout=api_connection_timeout, validate_cert=valid_cert_check)
        self.device_id = device_id

        self.sync_token = None
        self.sync_filter = '{ "room": { "timeline" : { "limit" : %i } } }' \
                           % sync_filter_limit
        self.token = token
        self.user_id = None
        self.home_server = None
        """ Time to wait before attempting a /sync request after failing."""
        self.rooms = {
            # room_id: Room
        }
        self.users = {
            # user_id: User
        }

    def login(self, username: str, password: str):
        """
        Login to the home server.

        Args:
            username (str): Account username
            password (str): Account password
        Returns:
            str: Access token
        Raises:
            MatrixRequestError
        """
        response = self.api.login(
            "m.login.password", user=username, password=password, device_id=self.device_id
        )
        self.user_id = response["user_id"]
        self.token = response["access_token"]
        self.home_server = response["home_server"]
        self.device_id = response["device_id"]
        self.api.token = self.token

        return self.token

    def logout(self):
        """
            Logout from the home server.
        """
        self.api.logout()

    # TODO: move room creation/joining to User class for future application service usage
    # NOTE: we may want to leave thin wrappers here for convenience
    def create_room(self, alias=None, is_public=False, invitees=None):
        """
        Create a new room on the home server.

        Args:
            alias (str): The canonical_alias of the room.
            is_public (bool):  The public/private visibility of the room.
            invitees (str[]): A set of user ids to invite into the room.

        Returns:
            Room

        Raises:
            MatrixRequestError
        """
        response = self.api.create_room(
            alias=alias, is_public=is_public, invitees=invitees)
        return self._make_room(response["room_id"])

    def join_room(self, room_id_or_alias):
        """
        Join a room.

        Args:
            room_id_or_alias (str): Room ID or an alias.

        Returns:
            Room

        Raises:
            MatrixRequestError
        """
        response = self.api.join_room(room_id_or_alias)
        room_id = (
            response["room_id"] if "room_id" in response else room_id_or_alias
        )
        return self._make_room(room_id)

    # TODO: move to User class. Consider creating lightweight Media class.
    def upload(self, content, content_type, filename=None):
        """ Upload content to the home server and receive a MXC url.

        Args:
            content (bytes): The data of the content.
            content_type (str): The mimetype of the content.
            filename (str): Optional. Filename of the content.

        Raises:
            MatrixUnexpectedResponse: If the home_server gave a strange response
            MatrixRequestError: If the upload failed for some reason.
        """
        try:
            response = self.api.media_upload(content, content_type, filename)
            if "content_uri" in response:
                return response["content_uri"]
            else:
                raise MatrixUnexpectedResponse(
                    "The upload was successful, but content_uri wasn't found."
                )
        except MatrixRequestError as e:
            raise MatrixRequestError(
                code=e.code,
                content="Upload failed: %s" % e
            )

    def _make_room(self, room_id):
        room = Room(self, room_id)
        self.rooms[room_id] = room
        return self.rooms[room_id]

    def sync(self, timeout_ms=30000):
        """
            For sync
        """
        response = self.api.sync(self.sync_token, timeout_ms=timeout_ms)
        self.sync_token = response["next_batch"]

        # for presence_update in response['presence']['events']:
        #     for callback in self.presence_listeners.values():
        #         callback(presence_update)

        # for room_id, invite_room in response['rooms']['invite'].items():
        #     for listener in self.invite_listeners:
        #         listener(room_id, invite_room['invite_state'])

        # for room_id, left_room in response['rooms']['leave'].items():
        #     for listener in self.left_listeners:
        #         listener(room_id, left_room)
        #     if room_id in self.rooms:
        #         del self.rooms[room_id]

        # if self._encryption and 'device_one_time_keys_count' in response:
        #     self.olm_device.update_one_time_key_counts(
        #         response['device_one_time_keys_count'])

        # for room_id, sync_room in response['rooms']['join'].items():
        #     if room_id not in self.rooms:
        #         self._make_room(room_id)
        #     room = self.rooms[room_id]
        #     # TODO: the rest of this for loop should be in room object method
        #     room.prev_batch = sync_room["timeline"]["prev_batch"]
        #
        #     for event in sync_room["state"]["events"]:
        #         event['room_id'] = room_id
        #         room._process_state_event(event)
        #
        #     for event in sync_room["timeline"]["events"]:
        #         event['room_id'] = room_id
        #         room._put_event(event)
        #
        #         # TODO: global listeners can still exist but work by each
        #         # room.listeners[uuid] having reference to global listener
        #
        #     for event in sync_room['ephemeral']['events']:
        #         event['room_id'] = room_id
        #         room._put_ephemeral_event(event)

    # TODO: move to Room class
    def remove_room_alias(self, room_alias):
        """Remove mapping of an alias

        Args:
            room_alias(str): The alias to be removed.

        Returns:
            bool: True if the alias is removed, False otherwise.
        """
        try:
            self.api.remove_room_alias(room_alias)
            return True
        except MatrixRequestError:
            return False
