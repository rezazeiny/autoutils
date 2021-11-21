# coding=utf-8
"""
    Redis functions
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import hashlib
import logging

from redis import StrictRedis

from autoutils.color import Color, get_color_text

logger = logging.getLogger(__name__)


class RedisHandler:
    """
    Handler Redis
    """

    def __init__(self, url: str, reset: bool = False):
        self.url = url
        self.reset = reset
        self.redis_cache = StrictRedis.from_url(self.url, decode_responses=True)

    def get(self, name: str, default=None, retry: int = 3) -> str:
        """
            easy function for handle cache
            :param retry: number of retry
            :param name: name of cache
            :param default: default value if not exist
            :return:
        """
        cache_data = "None"
        if retry <= 0:
            return cache_data
        if self.reset:
            logger.warning(f"{name} remove from cache")
            self.set(name, cache_data)
        try:
            cache_data = self.redis_cache.get(name)
        except Exception as e:
            logger.error(f"Error in get from cache e: {e}")
            return self.get(name=name, default=default, retry=retry - 1)
        if cache_data is None or cache_data == "None":
            logger.warning(f"{name} not found in cache. initialise it.")
            self.set(name, default)
        try:
            cache_data = self.redis_cache.get(name)
        except Exception as e:
            logger.error(f"Error in get from cache e: {e}")
            return self.get(name=name, default=default, retry=retry - 1)
        logger.warning(f"{name} is {cache_data}")
        return cache_data

    def check_hash(self, name: str, data_hash: str = None) -> bool:
        """
        check hash
        :param name:
        :param data_hash:
        :return:
        """
        if data_hash is None:
            return False
        saved_hash = self.get(name=name)
        return data_hash == saved_hash

    def find_hash(self, name: str, all_hash: dict = None) -> bool:
        """

        :param name:
        :param all_hash:
        :return:
        """
        if all_hash is None:
            return False
        return self.check_hash(name, all_hash.get(name, None))

    def set(self, name: str, value: str, retry: int = 3) -> str:
        """

        :param name:
        :param value:
        :param retry:
        :return:
        """
        value = str(value)
        if retry <= 0:
            return ""
        try:
            self.redis_cache.set(name, value)
        except Exception as e:
            logger.error(f"Error in set in cache. e: {e}")
            return self.set(name=name, value=value, retry=retry - 1)
        return value

    def set_hash(self, name: str, value) -> str:
        """

        :param name:
        :param value:
        :return:
        """
        return self.set(name, self.get_hash(value))

    @staticmethod
    def get_hash(value) -> str:
        """

        :param value:
        :return:
        """
        return hashlib.md5(str(value).encode()).hexdigest()
