"""
    Redis functions
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import hashlib
import logging
import time

from redis import StrictRedis

logger = logging.getLogger(__name__)


class RedisHandler:
    """
        Handler For redis database
    """

    def __init__(self, url, retry_count=3, retry_delay=2):
        """

        Args:
            url (str): redis server url
            retry_count (int) : how many retry in error condition
            retry_delay (int0 :
        """
        self.url = url
        self.redis_cache = StrictRedis.from_url(self.url, decode_responses=True)
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    def _get(self, key: str):
        try:
            return self.redis_cache.get(key)
        except Exception as e:
            logger.error(f"Error in get from cache e: {e}")
            return None

    def get(self, key, default=None, cast=None) -> str:
        """
            get value in redis
        Args:
            key (str): name of value in database
            default: default value
            cast: cast function
        Returns:
            (str) : value in redis

        """
        for i in range(self.retry_count):
            value = self._get(key=key)
            if value is None:
                time.sleep(self.retry_delay)
                continue
            if value is None or value == "None":
                logger.warning(f"{key} not found in cache. initialise it.")
                self.set(key, default)
            try:
                return cast(self._get(value))
            except Exception as e:
                logger.error(f"Error in get from cache e: {e}")
                return "None"
        return "None"

    def set(self, key, value) -> bool:
        """
            Set a value in redis
        Args:
            key (str): name of value
            value (str): value

        Returns:
            (bool) : str
        """
        value = str(value)
        for i in range(self.retry_count):
            try:
                self.redis_cache.set(key, value)
                return True
            except Exception as e:
                logger.error(f"Error in set in cache. e: {e}")
                time.sleep(self.retry_delay)
                continue
        return False

    def set_hash(self, key, data) -> bool:
        """
            Set hash of value in redis
        Args:
            key (str): name of key
            data (str): data
        Returns:
            (bool) : result
        """
        return self.set(key, self.get_hash(data))

    @staticmethod
    def get_hash(data) -> str:
        """
            Calculate hash of data

        Args:
            data : input data

        Returns:
            (str) : hash value
        """
        return hashlib.md5(str(data).encode()).hexdigest()

    def check_hash(self, key, data=None) -> bool:
        """
            Check hash of data by saved data
        Args:
            key (str): input key
            data: input data

        Returns:
            (bool) : result of checking
        """
        if data is None:
            return False
        saved_hash = self.get(key=key)
        return self.get_hash(data) == saved_hash
