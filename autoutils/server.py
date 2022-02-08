"""
    Server Work
"""
__author__ = ('Reza Zeiny <zeiny.r@yaftar.ir>',)

import inspect
import os
from datetime import datetime
from typing import Tuple, Optional

import paramiko

from .color import Colors, print_color

try:
    import requests
except ImportError:
    requests = None

from sshtunnel import SSHTunnelForwarder

import logging
import time

logger = logging.getLogger(__name__)


class CustomSSHClient:
    """
        additional need for ssh
    """

    def __init__(self, ssh):
        self.ssh: "paramiko.SSHClient" = ssh

    def execute(self, command: str) -> Tuple[int,
                                             paramiko.channel.ChannelStdinFile,
                                             paramiko.channel.ChannelFile,
                                             paramiko.channel.ChannelStderrFile]:
        """
            Execute a command and get process id
        """
        command = 'echo $$; exec ' + command
        stdin, stdout, stderr = self.ssh.exec_command(command)
        pid = int(stdout.readline())
        return pid, stdin, stdout, stderr

    def kill(self, pid: int, signal: int = 15):
        """
            Kill a process
        """
        self.ssh.exec_command(f"kill -{signal} {pid}")


class CustomSFTPClient:
    """
        additional need for sftp
    """

    def __init__(self, sftp):
        self.sftp: "paramiko.SFTPClient" = sftp

        # def put_dir(self, local, remote):
        """ 
            Uploads the contents of the local directory to the remote path. The
            remote directory needs to exists. All subdirectories in local are 
            created under remote.
        """
        # for item in os.listdir(local):
        #     if os.path.isfile(os.path.join(local, item)):
        #         self.put(os.path.join(local, item), '%s/%s' % (remote, item))
        #     else:
        #         self.mkdir('%s/%s' % (remote, item), ignore_existing=True)
        #         self.put_dir(os.path.join(local, item), '%s/%s' % (remote, item))

    def get_dir(self, remote: str, local: str = "./"):
        """
            Uploads the contents of the remote directory to the local path. The
            local directory needs to exists. All subdirectories in remote are
            created under local.
        """
        if not os.path.exists(local):
            os.mkdir(local)
        for item in self.sftp.listdir(remote):
            remote_path = os.path.join(remote, item)
            local_path = os.path.join(local, item)
            remote_path_stat = str(self.sftp.stat(remote_path))
            if remote_path_stat[0] != 'd':
                self.sftp.get(remote_path, local_path)
            else:
                if not os.path.exists(local_path):
                    os.mkdir(local_path)
                self.get_dir(remote_path, local_path)

        # def mkdir(self, path, mode=511, ignore_existing=False):
        """ 
            Augments mkdir by adding an option to not fail if the folder exists  
        """
        # try:
        #     super(MySFTPClient, self).mkdir(path, mode)
        # except IOError:
        #     if ignore_existing:
        #         pass
        #     else:
        #         raise


class Server:
    """
        For connect to server ether before mirror
        SSH DOCS: http://docs.paramiko.org/en/stable/api/agent.html
        SFTP DOCS: http://docs.paramiko.org/en/stable/api/sftp.html
    """

    def __init__(self, *, name: str = "server", middle_host: str = None, middle_port: int = 22,
                 middle_username: str = "user",
                 middle_password: str = "1", host: str = "localhost", port: int = 22, username: str = "user",
                 password: str = "1", handle=None, next_host: str = None, next_port: int = None):
        self.__name = str(name)
        self.__middle_host = middle_host
        self.__middle_port = middle_port
        self.__middle_username = middle_username
        self.__middle_password = middle_password
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__ssh_host = host
        self.__ssh_port = port
        self.__ssh: Optional["paramiko.SSHClient"] = None
        self.__sftp: Optional["paramiko.SFTPClient"] = None
        self.__handle = handle
        self.__next_host = None
        self.__next_port = None
        self.__tunnel_host = next_host
        self.__tunnel_port = next_port

        self.start_dt = None
        self.end_dt = None

        self.is_connect = None
        self.return_value = None
        self.has_exception = None
        self.connection_time = None

        if callable(handle):
            print_color("handle in server class is deprecated. use handle in start", color=Colors.RED_F)

    def __str__(self):
        return f"'{self.__name}' {self.__username}@{self.__host}:{self.__port}"

    def __log(self, level, message, data=None):
        if data is None:
            data = {}
        log_data = {"server": {
            "username": self.__username,
            "ip": self.__host,
            "port": self.__port,
            **data
        }}
        if logger.isEnabledFor(level):
            # noinspection PyProtectedMember
            logger._log(level, f"{self}: {message}", (log_data,))

    @staticmethod
    def test_handle(sftp: "paramiko.SFTPClient"):
        return sftp.listdir()

    def get_handle_data(self, handle, **kwargs):
        """
            For get useful data for handle function
        """
        if not callable(handle):
            return None
        # noinspection PyUnresolvedReferences
        args_data = inspect.getfullargspec(handle)
        handle_inputs = args_data.args
        use_kwargs = args_data.varkw is not None
        kwargs = {
            "name": self.__name,
            "ssh": self.__ssh,
            "sftp": self.__sftp,
            "ssh_host": self.__ssh_host,
            "ssh_port": self.__ssh_port,
            "next_host": self.__next_host,
            "next_port": self.__next_port,
            **kwargs
        }
        send_data = {}
        for key, value in kwargs.items():
            if key in handle_inputs or use_kwargs:
                send_data[key] = value
        return send_data

    def _run(self, handle, retry_count, retry_delay, **kwargs):
        """
            Run all work
        """
        self.__log(logging.INFO, f"Connected {self.__ssh_host}:{self.__ssh_port}")
        self.is_connect = True
        for i in range(retry_count):
            try:
                self.has_exception = False
                handle_data = self.get_handle_data(handle=handle, **kwargs)
                self.return_value = handle(**handle_data)
                break
            except Exception as e:
                self.has_exception = True
                self.__log(logging.ERROR, f"error in calling function {handle.__name__} with error {e}")
            if i < (retry_count - 1):
                time.sleep(retry_delay)
        return self.return_value

    def start(self, handle=None, retry_count=1, retry_delay=0, **kwargs):
        """
            Start working
        """
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        if handle is None:
            handle = self.__handle
        if handle is None:
            handle = self.test_handle
        if not callable(handle):
            self.__log(logging.ERROR, f"function {handle.__name__} is not callable")
            return
        self.is_connect = False
        self.start_dt = datetime.now()
        if self.__middle_host is None:
            self._set_connect(handle=handle, retry_count=retry_count, retry_delay=retry_delay, **kwargs)
        else:
            self._set_tunnel(handle=handle, retry_count=retry_count, retry_delay=retry_delay, **kwargs)
        self.end_dt = datetime.now()
        self.connection_time = (self.end_dt - self.start_dt).total_seconds()
        self.__log(logging.INFO, f"Run function {handle.__name__} is completed", data={
            "connection_time": self.connection_time,
            "is_connect": self.is_connect,
            "has_exception": self.has_exception
        })
        return self.return_value

    def _set_connect(self, handle, retry_count, retry_delay, **kwargs):
        """
            Start ssh connect
        """
        self.__log(logging.DEBUG, f"Start ssh {self.__ssh_host}:{self.__ssh_port}")
        try:
            if self.__tunnel_port is not None and self.__tunnel_host is not None:
                self.__log(logging.DEBUG, f"Start tunnel in for next host {self.__ssh_host}:{self.__ssh_port} => "
                                          f"{self.__tunnel_host}:{self.__tunnel_port}")
                with SSHTunnelForwarder(
                        ssh_address_or_host=(self.__ssh_host, self.__ssh_port),
                        ssh_username=self.__username,
                        ssh_password=self.__password,
                        remote_bind_address=(self.__tunnel_host, self.__tunnel_port),
                        set_keepalive=100, threaded=False) as tunnel:
                    self.__log(logging.DEBUG, f"Started tunneling success for next host "
                                              f"{tunnel.local_bind_host}:{tunnel.local_bind_port} => "
                                              f"{self.__tunnel_host}:{self.__tunnel_port}")
                    self.__next_host = tunnel.local_bind_host
                    self.__next_port = tunnel.local_bind_port
                    self._run(handle=handle, retry_count=retry_count, retry_delay=retry_delay, **kwargs)
                    self.__log(logging.DEBUG, f"Closing tunneling server for next host "
                                              f"{tunnel.local_bind_host}:{tunnel.local_bind_port} => "
                                              f"{self.__tunnel_host}:{self.__tunnel_port}")
            else:
                self.__ssh = paramiko.SSHClient()
                self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.__ssh.connect(self.__ssh_host, port=self.__ssh_port,
                                   username=self.__username,
                                   password=self.__password)
                self.__sftp: "paramiko.SFTPClient" = self.__ssh.open_sftp()
                self._run(handle=handle, retry_count=retry_count, retry_delay=retry_delay, **kwargs)
                try:
                    self.__ssh.close()
                    self.__log(logging.DEBUG, f"Closed {self.__ssh_host}:{self.__ssh_port}")
                except Exception as e:
                    self.__log(logging.ERROR, f"Error in closing ssh connection. error: {e}")

        except Exception as e:
            self.__log(logging.ERROR, f"Error in set connect. error: {e}")
        return self.return_value

    def _set_tunnel(self, handle, retry_count, retry_delay, **kwargs):
        """
            Start tunnel
        """
        self.__log(logging.DEBUG, f"Starting tunneling {self.__middle_host}:{self.__middle_port} => "
                                  f"{self.__host}:{self.__port}")
        with SSHTunnelForwarder(
                ssh_address_or_host=(self.__middle_host, self.__middle_port),
                ssh_username=self.__middle_username, ssh_password=self.__middle_password,
                remote_bind_address=(self.__host, self.__port),
                set_keepalive=100, threaded=False) as server:
            self.__ssh_host = server.local_bind_host
            self.__ssh_port = server.local_bind_port
            self.__log(logging.INFO, f"Started tunneling middle success "
                                     f"{self.__ssh_host}:{self.__ssh_port} => "
                                     f"{self.__host}:{self.__port}")
            self._set_connect(handle=handle, retry_count=retry_count, retry_delay=retry_delay, **kwargs)
            self.__log(logging.DEBUG, f"Closing tunneling "
                                      f"{self.__ssh_host}:{self.__ssh_port} => "
                                      f"{self.__host}:{self.__port}")
        return self.return_value
