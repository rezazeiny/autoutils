"""
    Easy tools for nice string and printing
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import logging
import os
from datetime import datetime
from enum import Enum
from typing import Tuple, List

try:
    from blessings import Terminal
except ImportError:
    Terminal = None

logger = logging.getLogger(__name__)


class Colors(Enum):
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


def get_colors(color=None, colors=None):
    """
        get color list
    Args:
        color (Colors): 
        colors (List[Colors]): 

    Returns:
        (str) : color list by string

    """
    result = ""
    if color is not None:
        result += color.value
    if colors is not None:
        for color in colors:
            result += color.value
    return result


def get_text(*args, sep=' '):
    """
        Use this function for join some data with a separator
    Args:
        *args: all arguments
        sep (str): text separator

    Returns:
        (str) : result text

    """
    text = ""
    for i in range(len(args)):
        text += str(args[i])
        if i != len(args) - 1:
            text += sep
    return text


def get_color_text(*args, color=None, colors=None, sep=' '):
    """
        Use this function for join some data with a separator and return colorful string
    Args:
        *args: all input arguments
        color (Colors): text color
        colors (List[Colors]): text colors
        sep (str): text separator

    Returns:
        (str) : result colorful text

    """
    text = get_text(*args, sep=sep)
    return f"{get_colors(color=color, colors=colors)}{text}{Colors.DEFAULT.value}"


def print_color(*args, end: str = '\n', color=None, colors=None, sep=' '):
    """
        Print colorful text
    Args:
        *args: all input arguments
        end (str): end text
        color (Colors): text color
        colors (List[Colors]): text colors 
        sep (str): text separator 

    Returns:
        (str) : printed text

    """
    printed_text = f"{get_color_text(*args, sep=sep, colors=colors, color=color)}"
    print(printed_text, end=end)
    return printed_text


class Progressbar:
    """
        Use this class for show progressbar in loop or etc.
    """

    def __init__(self, prefix="", suffix="", fill='█', not_fill='-', left_schema=" |", right_schema="| ", decimals=1,
                 show_time=False):
        """
            Progressbar initialize data
        Args:
            prefix (str): text shown before progressbar
            suffix (str): text shown after progressbar
            fill (str): a character shown for filling progressbar  
            not_fill (str): a character shown for not filled in progressbar
            left_schema (str): a character use for left of filling string 
            right_schema (str): a character use for right of not filling string 
            decimals (int): decimal point for completed percent
            show_time (bool): for showing elapsed and remaining time
        """
        self.prefix = prefix
        self.suffix = suffix
        self.fill = fill
        self.not_fill = not_fill
        self.left_schema = left_schema
        self.right_schema = right_schema
        self.decimals = decimals
        self.elapsed_time = ""
        self.remain_time = ""

        self.prefix_color = Colors.BRIGHT_MAGENTA_F
        self.suffix_color = Colors.MAGENTA_F
        self.fill_color = Colors.BLUE_F
        self.not_fill_color = Colors.YELLOW_F
        self.left_schema_color = Colors.RED_F
        self.right_schema_color = Colors.RED_F
        self.percent_color = Colors.CYAN_F
        self.time_color = Colors.GREEN_F

        self.is_print = False
        self.terminal = None
        self.show_time = show_time
        self.start_time = None
        self._set_start_time()
        if Terminal is not None:
            try:
                self.terminal = Terminal()
            except Exception as e:
                logger.error(f"You are not in terminal {e}")

    def _set_start_time(self):
        self.start_time = datetime.now()

    @property
    def _colored_prefix(self):
        return get_color_text(self.prefix, color=self.prefix_color)

    @property
    def _colored_suffix(self):
        return get_color_text(self.suffix, color=self.suffix_color)

    @property
    def _colored_fill(self):
        return get_color_text(self.fill, color=self.fill_color)

    @property
    def _colored_not_fill(self):
        return get_color_text(self.not_fill, color=self.not_fill_color)

    @property
    def _colored_left_schema(self):
        return get_color_text(self.left_schema, color=self.left_schema_color)

    @property
    def _colored_right_schema(self):
        return get_color_text(self.right_schema, color=self.right_schema_color)

    @property
    def _colored_elapsed_time(self):
        return get_color_text(self.elapsed_time, color=self.time_color)

    @property
    def _colored_remain_time(self):
        return get_color_text(self.remain_time, color=self.time_color)

    def _get_percent(self, iteration: int, total: int) -> Tuple[str, int]:
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
        length = self._terminal_size - len(percent) - minus_len
        return get_color_text(percent, color=self.percent_color), length

    # noinspection PyBroadException
    @property
    def _terminal_size(self):
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

    def print(self, iteration, total):
        """
            Print progressbar
            if total >= iteration go to next line
        Args:
            iteration (int): current position of progressbar
            total (int): total data count for progressbar

        Returns:


        """
        if iteration <= 1:
            self._set_start_time()
        if self._terminal_size == -1:
            print("-", end="")
        else:
            percent, length = self._get_percent(iteration=iteration, total=total)
            filled_length = int(length * iteration // total)
            print(
                self._colored_elapsed_time,
                self._colored_prefix,
                self._colored_left_schema,
                self._colored_fill * filled_length,
                self._colored_not_fill * (length - filled_length),
                self._colored_right_schema,
                percent,
                self._colored_suffix,
                self._colored_remain_time,
                sep="", end="\r")

        # Print New Line on Complete
        if iteration <= total:
            print()
