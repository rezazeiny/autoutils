"""
    working with file easily
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import gzip
import json
import logging
import os
import pickle
from enum import Enum

logger = logging.getLogger(__name__)


class FileModes(Enum):
    """
        Type of Files
    """
    NORMAL = "normal"
    JSON = "json"
    GZIP = "gzip"
    OBJECT = "object"
    FILE = "file"
    APPEND = "append"


def read_file(address, file_mode=FileModes.NORMAL):
    """
        easy way to read file
    Args:
        address (str): file address
        file_mode (FileModes): mode of reading

    Returns:
        file data

    """
    if address is None:
        return None
    logger.debug(f"reading file. addr: {address} {file_mode}")
    mode = "r"
    if file_mode in [FileModes.OBJECT, FileModes.FILE]:
        mode = "rb"
    try:
        if file_mode == FileModes.GZIP:
            with gzip.open(address) as file:
                file_data = []
                for line in file.readlines():
                    try:
                        file_data.append(line.strip().decode("UTF-8"))
                    except UnicodeDecodeError:
                        pass
        else:
            with open(address, mode) as file:
                if file_mode == FileModes.JSON:
                    file_data = json.load(file)
                elif file_mode == FileModes.OBJECT:
                    file_data = pickle.load(file)
                elif file_mode == FileModes.FILE:
                    file_data = file.read()
                elif file_mode == FileModes.NORMAL:
                    file_data = [s.strip() for s in file.readlines()]

        logger.debug(f"reading file is complete. addr: {address} {file_mode}")
        return file_data
    except Exception as e:
        logger.error(f"reading file {address} failed e: {e}")
        return None


def write_file(address: str, data, file_mode=FileModes.NORMAL) -> bool:
    """
        Write or append easily to file
    Args:
        address (str): file address
        data: data
        file_mode (FileModes): file mode

    Returns:
        (bool) : job state
    """
    if address is None:
        return False

    if type(data) == str and file_mode in [FileModes.APPEND, FileModes.NORMAL]:
        data = [data]

    mode = "w"
    if file_mode == FileModes.APPEND:
        mode = "a+"
    elif file_mode in [FileModes.OBJECT, FileModes.FILE]:
        mode = "wb"
    logger.debug(f"mode: {file_mode}, addr: {address}")

    try:
        with open(address, mode) as file:
            if file_mode == FileModes.JSON:
                json.dump(data, file, indent=4, sort_keys=True, ensure_ascii=False)
            elif file_mode == FileModes.OBJECT:
                pickle.dump(data, file)
            elif file_mode == FileModes.FILE:
                file.write(data)
            else:
                for line in data:
                    file.write(str(line) + "\n")
        logger.debug(f"{file_mode} is complete. addr: {address}")

        return True
    except Exception as e:
        logger.error(f"{file_mode} fail. addr: {address}, e: {e}")
    return False


def remove_file_if_exists(path) -> bool:
    """
        Remove File if exists
        Args:
            path (str) : file path
        Returns:
            (bool) : remove state
    """
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
