"""
    Log
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import json
import logging
from typing import List, Optional

import requests

from .color import get_color_text, print_color, Colors

try:
    # noinspection PyPep8Naming
    from persiantools.jdatetime import JalaliDateTime as datetime
except ImportError:
    print_color("Install persiantools library with pip install", color=Colors.RED_F)
    from datetime import datetime

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

is_set_logger: bool = False


class Logger:
    """
        Logger Class
    """
    logger = None
    app_name: str = None
    host: str = None
    extra_data: dict = None

    log_level: int = INFO
    log_format = '%(datetime)s %(level)s%(process_thread)s%(file_detail)s%(text)s'

    colorful: bool = True
    show_datetime: bool = True
    datetime_color: "Colors" = Colors.GREEN_F

    file_depth: int = 1
    show_file: bool = True
    show_line: bool = True
    show_func: bool = True
    file_color: "Colors" = Colors.MAGENTA_F

    show_process_name: bool = False
    show_process_id: bool = False
    show_thread_name: bool = False
    show_thread_id: bool = False
    process_thread_color: "Colors" = Colors.BLUE_F

    show_level: bool = True
    level_detail = {
        NOTSET: ("NOTSET   ", Colors.CYAN_F),
        CRITICAL: ("CRITICAL ", Colors.BRIGHT_RED_F),
        ERROR: ("ERROR    ", Colors.RED_F),
        WARNING: ("WARNING  ", Colors.BLUE_F),
        INFO: ("INFO     ", Colors.BRIGHT_CYAN_F),
        DEBUG: ("DEBUG    ", Colors.BRIGHT_MAGENTA_F),
    }

    log_server: str = None

    old_factory = None

    @classmethod
    def get_logger(cls, name: str, log_level: int = None):
        """
            For get logger
        """
        global is_set_logger
        cls.logger = logging.getLogger(name)
        if is_set_logger:
            return cls.logger
        if log_level is None:
            log_level = cls.log_level
        logging.basicConfig(format=cls.log_format, level=log_level)
        cls.old_factory = logging.getLogRecordFactory()
        logging.setLogRecordFactory(cls.record_factory)
        is_set_logger = True
        return cls.logger

    @classmethod
    def add_file_handler(cls, file_address: str, log_level=ERROR):
        """
            Add File Handler
        """
        if cls.logger is None:
            print_color("no logger found", color=Colors.RED_F)
            return
        handler = logging.FileHandler(file_address)
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter(cls.log_format))
        cls.logger.addHandler(handler)

    @staticmethod
    def get_inner_detail(data_list: List[tuple], sep: str = ":"):
        """
            For remove repeat
        """
        detail = ""
        last_cond = False
        for i in range(len(data_list)):
            cond, data = data_list[i]
            if cond:
                if last_cond:
                    detail += sep
                detail += str(data)
            last_cond = cond
        return detail

    @staticmethod
    def get_outer_detail(data_list: [str], sep: str = " - "):
        """
            For remove repeat
        """
        detail = ""
        last_cond = False
        for i in range(len(data_list)):
            data = data_list[i]
            cond = data != ""
            if cond and last_cond:
                detail += sep
            detail += str(data)
            last_cond = cond
        if detail != "":
            return "[ " + detail + " ] "
        else:
            return detail

    @classmethod
    def get_color_text(cls, text, color: Optional[Colors]):
        """
            Get Color Text
        """
        if cls.colorful:
            return get_color_text(text, color=color)
        else:
            return str(text)

    @classmethod
    def get_datetime(cls):
        """
            Get Time
        """
        return cls.get_inner_detail([
            (cls.show_datetime, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ])

    @classmethod
    def get_process_thread(cls, record):
        """
            Process and thread detail
        """
        process_detail = cls.get_inner_detail([
            (cls.show_process_name, record.processName),
            (cls.show_process_id, record.process)
        ])
        thread_detail = cls.get_inner_detail([
            (cls.show_thread_name, record.threadName),
            (cls.show_thread_id, record.thread)
        ])
        return cls.get_outer_detail([process_detail, thread_detail])

    @classmethod
    def get_file_detail(cls, record: logging.LogRecord):
        """
            Get File and line detail
        """
        file_detail = cls.get_inner_detail([
            (cls.show_file, "/".join(record.pathname.split("/")[-cls.file_depth:])),
            (cls.show_line, record.lineno),
        ])
        function_detail = cls.get_inner_detail([
            (cls.show_func, record.module + "()"),
        ])
        return cls.get_outer_detail([file_detail, function_detail])

    @classmethod
    def get_level(cls, record):
        """
            Get Level
        """
        return cls.get_inner_detail([
            (cls.show_level, cls.level_detail.get(record.levelno, ("",))[0])
        ])

    @classmethod
    def get_level_color(cls, record):
        """
            Get Level Color
        """
        return cls.level_detail.get(record.levelno, ("", Colors.YELLOW_B))[1]

    @classmethod
    def record_factory(cls, *args, **kwargs):
        """
        for change some value
        :param args:
        :param kwargs:
        :return:
        """
        new_args = list(args)
        message = str(new_args[4])
        message_args = new_args[5]
        extra_args = False
        if len(message_args) == 1 and "%s" not in message and "%d" not in message:
            new_args[4] += " %s"
            extra_args = True
        record = cls.old_factory(*tuple(new_args), **kwargs)
        record.datetime = cls.get_color_text(cls.get_datetime(), color=cls.datetime_color)
        record.process_thread = cls.get_color_text(cls.get_process_thread(record), color=cls.process_thread_color)
        record.file_detail = cls.get_color_text(cls.get_file_detail(record), color=cls.file_color)

        record.short_message = None
        record.full_message = None
        if type(record.msg) == dict:
            record.full_message = record.msg
        elif extra_args:
            record.short_message = args[4]
            data_args = new_args[5]
            if type(data_args[0]) == dict:
                record.full_message = data_args[0]
            else:
                record.full_message = str(data_args[0])
        else:
            # noinspection PyBroadException
            try:
                record.short_message = str(record.msg) % record.args
            except Exception:
                pass
        record.short_message = str(record.short_message)
        color = cls.get_level_color(record)
        record.level = cls.get_color_text(cls.get_level(record), color=color)
        record.text = cls.get_color_text(record.short_message, color=color)

        cls.send_to_log_server(record=record)
        return record

    @classmethod
    def get_send_data(cls, record: "logging.LogRecord"):
        """
            Get some log data
        """
        return {
            "level": record.levelno,
            "line": record.lineno,
            "file": record.filename,
            "level_name": record.levelname,
            "pathname": record.pathname,
            "thread": record.thread,
            "threadName": record.threadName,
            "process": record.process,
            "processName": record.processName,
            "function": record.module,
            "logger_name": record.name,
            "created": record.created,
            "msecs": record.msecs,
        }

    @classmethod
    def handle_log_server(cls, send_data):
        """
            For send data
        """
        if cls.log_server is None:
            return

        log_server = []
        if type(cls.log_server) == str:
            log_server = [cls.log_server]
        elif type(cls.log_server) in [list, tuple]:
            log_server = cls.log_server

        for server in log_server:
            try:
                headers = {"Content-Type": "application/json"}
                data = json.dumps(send_data)
                requests.post(server, data=data, headers=headers)
            except Exception as e:
                print_color(f"error in send data to log server {server}", e, color=Colors.RED_F)

    @classmethod
    def send_to_log_server(cls, record: "logging.LogRecord"):
        """
            Send Data to log server
        """
        if not cls.log_server:
            return
        short_message = record.__dict__.get("short_message")
        full_message = record.__dict__.get("full_message")
        send_data = {
            "short_message": short_message,
            "logger_data": cls.get_send_data(record)
        }
        if cls.app_name is not None:
            send_data["app_name"] = cls.app_name
        if cls.host is not None:
            send_data["host_name"] = cls.host
        if cls.extra_data is not None:
            send_data["extra_data"] = cls.extra_data
        urllib3_log = logging.getLogger("urllib3")
        urllib3_log.setLevel(logging.CRITICAL)
        urllib3_log.propagate = False

        if type(full_message) == dict:
            full_message = dict(full_message)
            for key, value in full_message.items():
                if str(key) not in ["logger_data", "extra_data", "short_message", "app_name", "host_name"]:
                    send_data[str(key)] = value

        cls.handle_log_server(send_data=send_data)
