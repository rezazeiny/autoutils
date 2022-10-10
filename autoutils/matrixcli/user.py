"""
    User
"""


def check_user_id(user_id: str):
    """
    For check user id string
    :param user_id:
    """
    if not user_id.startswith("@"):
        raise ValueError("UserIDs start with @")

    if ":" not in user_id:
        raise ValueError("UserIDs must have a domain component, separated by a :")


class User(object):
    """ The User class can be used to call user specific functions.
    """

    def __init__(self, api, user_id: str, display_name: str = None):
        check_user_id(user_id)

        self.user_id = user_id
        self.display_name = display_name
        self.api = api

    def get_display_name(self, room=None):
        """Get this user's display name.

        Args:
            room (Room): Optional. When specified, return the display name of the user
                in this room.

        Returns:
            The display name. Defaults to the user ID if not set.
        """
        if room:
            try:
                return room.members_display_names[self.user_id]
            except KeyError:
                return self.user_id
        if not self.display_name:
            self.display_name = self.api.get_display_name(self.user_id)
        return self.display_name or self.user_id

    def set_display_name(self, display_name):
        """ Set this users display name.

        Args:
            display_name (str): Display Name
        """
        self.display_name = display_name
        return self.api.set_display_name(self.user_id, display_name)
