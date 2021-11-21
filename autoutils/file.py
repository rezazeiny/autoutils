"""
    working with file
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import gzip
import json
import logging
import os
import pickle

logger = logging.getLogger(__name__)


class FILE_MODES:
    """
        Type of Files
    """
    NORMAL = "normal"
    JSON = "json"
    GZIP = "gzip"
    OBJECT = "object"
    FILE = "file"
    APPEND = "append"


def read_file(address: str, delete: bool = False,
              is_json: bool = False, is_gzip: bool = False, is_obj: bool = False,
              file_mode: FILE_MODES = FILE_MODES.NORMAL):
    """
    read a file
    :param address: address of file
    :param file_mode: file mode
    :param is_obj: if you want to read object
    :param is_json: if you want to read json file
    :param is_gzip: if you want to read gzip file
    :param delete: if you want to delete file
    :return: content of file or None for not exist file
    """
    if address is None:
        return None
    if is_json:
        logger.warning("is_json in read_file is deprecated. use file_mode parameter")
        file_mode = FILE_MODES.JSON
    if is_gzip:
        logger.warning("is_gzip in read_file is deprecated. use file_mode parameter")
        file_mode = FILE_MODES.GZIP
    if is_obj:
        logger.warning("is_obj in read_file is deprecated. use file_mode parameter")
        file_mode = FILE_MODES.OBJECT

    logger.debug(f"reading file. addr: {address} {file_mode}")
    mode = "r"
    if file_mode in [FILE_MODES.OBJECT, FILE_MODES.FILE]:
        mode = "rb"
    try:
        if file_mode == FILE_MODES.GZIP:
            with gzip.open(address) as file:
                file_data = []
                for line in file.readlines():
                    try:
                        file_data.append(line.strip().decode("UTF-8"))
                    except UnicodeDecodeError:
                        pass
        else:
            with open(address, mode) as file:
                if file_mode == FILE_MODES.JSON:
                    file_data = json.load(file)
                elif file_mode == FILE_MODES.OBJECT:
                    file_data = pickle.load(file)
                elif file_mode == FILE_MODES.FILE:
                    file_data = file.read()
                elif file_mode == FILE_MODES.NORMAL:
                    file_data = [s.strip() for s in file.readlines()]

        logger.debug(f"reading file is complete. addr: {address} {file_mode}")
        try:
            if delete and os.path.exists(address):
                os.remove(address)
        except Exception as e:
            logger.error(f"reading file {address} error in delete e: {e}")
        return file_data
    except Exception as e:
        logger.error(f"reading file {address} failed e: {e}")
        return None


def write_file(address: str, data,
               is_json: bool = False, is_obj: bool = False, append: bool = False,
               file_mode: FILE_MODES = FILE_MODES.NORMAL) -> bool:
    """
    write or append data to file
    :param address: address of file
    :param is_json: if you want write json mode
    :param is_obj: if you want write object mode
    :param data: data for store
    :param file_mode: file_mode
    :param append:
    """
    if address is None:
        return False
    if append:
        logger.warning("append in write_file is deprecated. use file_mode parameter")
        file_mode = FILE_MODES.APPEND
    if is_json:
        logger.warning("is_json in write_file is deprecated. use file_mode parameter")
        file_mode = FILE_MODES.JSON
    if is_obj:
        logger.warning("is_obj in write_file is deprecated. use file_mode parameter")
        file_mode = FILE_MODES.OBJECT

    if type(data) == str and file_mode in [FILE_MODES.APPEND, FILE_MODES.NORMAL]:
        data = [data]

    mode = "w"
    if file_mode == FILE_MODES.APPEND:
        mode = "a+"
    elif file_mode == FILE_MODES.OBJECT:
        mode = "wb"
    logger.debug(f"mode: {file_mode}, addr: {address}")

    try:
        with open(address, mode) as file:
            if file_mode == FILE_MODES.JSON:
                json.dump(data, file, indent=4, sort_keys=True, ensure_ascii=False)
            elif file_mode == FILE_MODES.OBJECT:
                pickle.dump(data, file)
            else:
                for line in data:
                    file.write(str(line) + "\n")
        logger.debug(f"{file_mode} is complete. addr: {address}")

        return True
    except Exception as e:
        logger.error(f"{file_mode} fail. addr: {address}, e: {e}")
    return False
