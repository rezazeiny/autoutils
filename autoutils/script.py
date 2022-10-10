"""
    All Work with linux scripting
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import logging
import random
import string
import subprocess
from threading import Thread

logger = logging.getLogger(__name__)

PIPE = -1
STDOUT = -2
DEVNULL = -3


def id_generator(size: int = 6, chars: list = string.ascii_uppercase + string.ascii_lowercase + string.digits) -> str:
    """
        Generate random string
    Args:
        size (int): size of random string
        chars (list): define select set

    Returns:
        (str) : random string
    """
    return ''.join(random.choice(chars) for _ in range(size))


class ShellScript:
    """
        Shell Script
    """

    def __init__(self, command, *, shell=False, text=True, split_stdout=True, split_stderr=True, timeout=None,
                 background=False, quiet=False, extra_data=None):
        self.__used = False
        self.command = command
        self.is_running = False
        self.process_id = None
        self.exit_code = None
        self.stdout = None
        self.stderr = None
        self.error = None

        self.shell = shell
        self.split_stdout = split_stdout
        self.split_stderr = split_stderr
        self.text = text
        self.timeout = timeout
        self.background = background
        self.quiet = quiet
        self.extra_data = extra_data

    def _log(self, level, message, data=None):
        if data is None:
            data = {}
        if logger.isEnabledFor(level):
            # noinspection PyProtectedMember
            logger._log(level, f"run {self.command}: {message}", (data,))

    def _run_job(self):
        self.is_running = True
        self._log(logging.DEBUG, "Start")
        if self.quiet:
            stderr = DEVNULL
            stdout = DEVNULL
        else:
            stdout = PIPE
            stderr = PIPE
        try:
            process = subprocess.Popen(self.command, shell=self.shell, text=self.text, stdout=stdout, stderr=stderr)
            self.process_id = process.pid
            self._on_start()
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
            except Exception as e:
                process.kill()
                raise e
            if stdout is not None:
                if self.text:
                    self.stdout = stdout
                else:
                    self.stdout = stdout.decode()
                if self.split_stdout:
                    self.stdout = self.stdout.split("\n")[:-1]
            if stderr is not None:
                if self.text:
                    self.stderr = stderr
                else:
                    self.stderr = stderr.decode()
                if self.split_stderr:
                    self.stderr = self.stderr.split("\n")[:-1]
            self.exit_code = process.poll()
            self.is_running = False
            if self.exit_code == 0:
                self._log(logging.DEBUG, "Completed")
                self._on_success()
            else:
                self._log(logging.DEBUG, f"Error Code {self.exit_code}")
                self._on_error()
        except Exception as e:
            self.is_running = False
            self.error = e
            self._log(logging.DEBUG, f"Exception {e}")
            self._on_exception()
        return self

    def _on_start(self):
        """
            If command is starting
        """
        pass

    def _on_error(self):
        """
            If exit code of running command is not zero call this function
        """
        pass

    def _on_success(self):
        """
            If exit code of running command is zero call this function
        """
        pass

    def _on_exception(self):
        """
            If acquire any exception while running command call this function
        """
        pass

    def run(self):
        """
            Run Script
        """
        if self.__used:
            raise Exception("this command was run before. make a new instance")
        self.__used = True

        if self.background:
            job = Thread(target=self._run_job)
            job.start()
            while self.process_id is None and self.error is None:
                pass
        else:
            self._run_job()
        return self
