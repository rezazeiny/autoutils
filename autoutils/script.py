"""
    All Work with linux scripting
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import logging
import random
import string
import subprocess

from .color import get_text

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


class RunScriptResult:
    """
        Object for run_script result
    """

    def __init__(self):
        self.command = None
        self.process_id = None
        self.exit_code = None
        self.stdout = None
        self.stderr = None
        self.error = None


def run_script(*args, timeout=None, background=False, quiet=False) -> "RunScriptResult":
    """
        Run Shell script in linux
    Args:
        *args: input command
        timeout (int): timeout for running command
        background (bool): run command in background
        quiet (bool): run command without any result
    Returns:
        (RunScriptResult) : result object
    """
    """
    :param save_output: for return output
    :param quiet: for run in quiet mode
    :param timeout: timeout
    :param background: background run
    :return: output_code output_content
    """
    result = RunScriptResult()
    result.command = get_text(*args)
    if background:
        result.command += " &"
    if quiet:
        stderr = DEVNULL
        stdout = DEVNULL
    else:
        stdout = PIPE
        stderr = PIPE
    logger.debug(f"run [{result.command}]: Start")

    try:
        with subprocess.Popen(result.command, shell=True, stdout=stdout, stderr=stderr) as process:
            result.process_id = process.pid
            stdout, stderr = "", ""
            try:
                if background:
                    process.wait(timeout=timeout)
                else:
                    stdout, stderr = process.communicate(timeout=timeout)
            # except subprocess.TimeoutExpired as e:
            #     process.kill()
            except Exception as e:  # Including KeyboardInterrupt, TimeoutExpired, communicate handled that.
                process.kill()
                raise e
            result.exit_code = process.poll()
            if result.exit_code == 0:
                logger.debug(f"run [{result.command}]: Complete")
            else:
                logger.debug(f"run [{result.command}]: Error Code: {result.exit_code}")
            if stdout is not None:
                if type(stdout) == bytes:
                    result.stdout = stdout.decode().split("\n")[:-1]
                else:
                    result.stdout = []
            if stderr is not None:
                if type(stderr) == bytes:
                    result.stderr = stderr.decode().split("\n")[:-1]
                else:
                    result.stderr = []
    except Exception as e:
        logger.error(f"error in run_script. e: {e}")
        result.error = e
    return result
