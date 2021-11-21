"""
    All Work with linux scripting
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import logging
import random
import string
import subprocess

from .color import get_text

PIPE = -1
STDOUT = -2
DEVNULL = -3

logger = logging.getLogger(__name__)


def id_generator(size: int = 6, chars: list = string.ascii_uppercase + string.ascii_lowercase + string.digits) -> str:
    """
    get random output
    :param size: length of random string
    :param chars: random set
    :return:
    """
    return ''.join(random.choice(chars) for _ in range(size))


def run_script(*args, timeout: int = None, background: bool = False, quiet: bool = False, save_output: bool = True
               ) -> dict:
    """
    :param save_output: for return output
    :param quiet: for run in quiet mode
    :param timeout: timeout
    :param background: background run
    :return: output_code output_content
    """
    output = {
        "pid": None,
        "result": None,
        "stdout": None,
        "stderr": None,
        "error": None,
    }
    script = get_text(*args)
    if background:
        script += " &"
    stdout = None
    stderr = None
    if quiet:
        stderr = DEVNULL
        stdout = DEVNULL
    elif save_output:
        stdout = PIPE
        stderr = PIPE
    logger.debug(f"run [{script}]: Start")

    try:
        with subprocess.Popen(script, shell=True, stdout=stdout, stderr=stderr) as process:
            output["pid"] = process.pid
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
            result = process.poll()
            output["result"] = result
            if output["result"] == 0:
                logger.debug(f"run [{script}]: Complete")
            else:
                logger.debug(f"run [{script}]: Error Code: {result}")
            if stdout is not None:
                if type(stdout) == bytes:
                    output["stdout"] = stdout.decode().split("\n")[:-1]
                else:
                    output["stdout"] = []
            if stderr is not None:
                if type(stderr) == bytes:
                    output["stderr"] = stderr.decode().split("\n")[:-1]
                else:
                    output["stderr"] = []
    except Exception as e:
        logger.error("error in run_script. e: %s", e)
        output["error"] = e
    return output
