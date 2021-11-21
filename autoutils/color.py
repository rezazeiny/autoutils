"""
    Easy tools for nice log and printing
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import logging
import os
from datetime import datetime
from typing import Tuple

try:
    from blessings import Terminal
except ImportError:
    Terminal = None

logger = logging.getLogger(__name__)


class Color:
    """
    All Color for beautiful result
    """
    DEFAULT = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NO_UNDERLINE = '\033[24m'
    NEGATIVE = '\033[7m'
    POSITIVE = '\033[27m'
    BLACK_F = '\033[30m'
    RED_F = '\033[31m'
    GREEN_F = '\033[32m'
    YELLOW_F = '\033[33m'
    BLUE_F = '\033[34m'
    MAGENTA_F = '\033[35m'
    CYAN_F = '\033[36m'
    WHITE_F = '\033[37m'
    EXTENDED_F = '\033[38m'
    DEFAULT_F = '\033[39m'
    BLACK_B = '\033[40m'
    RED_B = '\033[41m'
    GREEN_B = '\033[42m'
    YELLOW_B = '\033[43m'
    BLUE_B = '\033[44m'
    MAGENTA_B = '\033[45m'
    CYAN_B = '\033[46m'
    WHITE_B = '\033[47m'
    EXTENDED_B = '\033[48m'
    DEFAULT_B = '\033[49m'
    BRIGHT_BLACK_F = '\033[90m'
    BRIGHT_RED_F = '\033[91m'
    BRIGHT_GREEN_F = '\033[92m'
    BRIGHT_YELLOW_F = '\033[93m'
    BRIGHT_BLUE_F = '\033[94m'
    BRIGHT_MAGENTA_F = '\033[95m'
    BRIGHT_CYAN_F = '\033[96m'
    BRIGHT_WHITE_F = '\033[97m'
    BRIGHT_BLACK_B = '\033[100m'
    BRIGHT_RED_B = '\033[101m'
    BRIGHT_GREEN_B = '\033[102m'
    BRIGHT_YELLOW_B = '\033[103m'
    BRIGHT_BLUE_B = '\033[104m'
    BRIGHT_MAGENTA_B = '\033[105m'
    BRIGHT_CYAN_B = '\033[106m'
    BRIGHT_WHITE_B = '\033[107m'


def get_text(*args, sep: str = ' ') -> str:
    """
    :param args: input data
    :param sep: sep
    """
    text = ""
    for i in range(len(args)):
        text += str(args[i])
        if i != len(args) - 1:
            text += sep
    return text


def get_color_text(*args, color=Color.DEFAULT, **kwargs) -> str:
    """
    Print Colorful text
    :param color:
    """
    text = get_text(*args, **kwargs)
    colors = ""
    if type(color) == str:
        colors = color
    elif type(color) == list:
        for c in color:
            if type(c) == str:
                colors += c
    return colors + text + Color.DEFAULT


def print_color(*args, end: str = '\n', **kwargs) -> None:
    """
    Print Colorful text
    :param end:
    """
    print(get_color_text(*args, **kwargs), end=end)


# noinspection PyMissingOrEmptyDocstring
class Progressbar:
    """
    Call in a loop to create terminal progress bar
    """

    def __init__(self, prefix: str = "", suffix: str = "",
                 fill: str = '█', not_fill: str = '-',
                 left_schema: str = " |", right_schema: str = "| ",
                 decimals: int = 1,
                 not_terminal: bool = False, show_time=False):
        self.prefix = prefix
        self.suffix = suffix
        self.fill = fill
        self.not_fill = not_fill
        self.left_schema = left_schema
        self.right_schema = right_schema
        self.decimals = decimals
        self.elapsed_time = ""
        self.remain_time = ""

        self.prefix_color = Color.BRIGHT_MAGENTA_F
        self.suffix_color = Color.MAGENTA_F
        self.fill_color = Color.BLUE_F
        self.not_fill_color = Color.YELLOW_F
        self.left_schema_color = Color.RED_F
        self.right_schema_color = Color.RED_F
        self.percent_color = Color.CYAN_F
        self.time_color = Color.GREEN_F

        self.is_print = False
        self.terminal = None
        self.not_terminal = not_terminal
        self.show_time = show_time
        self.start_time = None
        self.set_start_time()
        if Terminal is not None:
            try:
                self.terminal = Terminal()
            except Exception as e:
                logger.error(f"You are not in terminal {e}")

    def set_start_time(self):
        self.start_time = datetime.now()

    @property
    def colored_prefix(self):
        return get_color_text(self.prefix, color=self.prefix_color)

    @property
    def colored_suffix(self):
        return get_color_text(self.suffix, color=self.suffix_color)

    @property
    def colored_fill(self):
        return get_color_text(self.fill, color=self.fill_color)

    @property
    def colored_not_fill(self):
        return get_color_text(self.not_fill, color=self.not_fill_color)

    @property
    def colored_left_schema(self):
        return get_color_text(self.left_schema, color=self.left_schema_color)

    @property
    def colored_right_schema(self):
        return get_color_text(self.right_schema, color=self.right_schema_color)

    @property
    def colored_elapsed_time(self):
        return get_color_text(self.elapsed_time, color=self.time_color)

    @property
    def colored_remain_time(self):
        return get_color_text(self.remain_time, color=self.time_color)

    def get_percent(self, iteration: int, total: int) -> Tuple[str, int]:
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        self.elapsed_time = ""
        self.remain_time = ""
        if self.show_time:
            self.elapsed_time = f"elapsed {int(elapsed_time)} "
            if iteration > 0:
                remain_time = (elapsed_time * (total - iteration) / iteration) + 1
                self.remain_time = f" remain {int(remain_time)}"

        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (iteration / float(total))) + "% "
        minus_len = (len(self.prefix) + len(self.left_schema) + len(self.right_schema) + len(self.suffix) +
                     len(self.remain_time) + len(self.elapsed_time))
        length = self.terminal_size - len(percent) - minus_len
        return get_color_text(percent, color=self.percent_color), length

    # noinspection PyBroadException
    @property
    def terminal_size(self):
        """
        update terminal size
        :return:
        """
        try:
            if self.terminal is None:
                terminal_size = os.get_terminal_size().columns
            else:
                terminal_size = self.terminal.width
            if terminal_size is None:
                raise TypeError
        except Exception:
            return -1
        return terminal_size

    def print(self, iteration: int, total: int):
        """
        Print progressbar
        :param iteration:
        :param total:
        :return:
        """
        if iteration <= 1:
            self.set_start_time()
        if self.terminal_size == -1:
            print("-", end="")
        else:
            percent, length = self.get_percent(iteration=iteration, total=total)
            filled_length = int(length * iteration // total)
            print(
                self.colored_elapsed_time,
                self.colored_prefix,
                self.colored_left_schema,
                self.colored_fill * filled_length,
                self.colored_not_fill * (length - filled_length),
                self.colored_right_schema,
                percent,
                self.colored_suffix,
                self.colored_remain_time,
                sep="", end="\r")

        # sys.stdout.write("\033[F")
        # Print New Line on Complete
        if iteration == total:
            print()


def print_progressbar(iteration: int, total: int, **kwargs):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        fill        - Optional  : bar fill character (Str)
    """
    Progressbar(**kwargs).print(iteration, total)
