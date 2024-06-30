from argparse import OPTIONAL, SUPPRESS, ZERO_OR_MORE
import re
import rich_argparse
from rich.text import Text
from rich.containers import Lines


def split_formatted_text(text: Text, width: int):
    plain_text = text.plain
    last_whitespace_index = -1
    current_width = 0
    splits: list[int] = []
    for index, character in enumerate(plain_text):
        if current_width > width:
            # throw if width has been breached
            raise AssertionError("Exceeded available width")
        if current_width >= width:
            # if current_width is euqal to width
            # add a splitting index
            if last_whitespace_index >= 0:
                # there as a whitespace
                # break after the last word
                # (this includes the space in the last word)
                splits.append(last_whitespace_index)
                current_width = index - last_whitespace_index
            else:
                # no whitespace in given part
                # cannot break before the word, break in the middle
                splits.append(index)
                current_width = 0
            # any splitter addition requires resetting last_whitespace_index
            last_whitespace_index = -1
        if character == "\n":
            # new line, so we have to split here anyways
            # current width is completely reset
            # index + 1 because we want the newline to be at the end of the part
            # this way we can remove it with rstrip()
            # ALSO DO NOT add +1 to current_width
            splits.append(index + 1)
            current_width = 0
            last_whitespace_index = -1
            continue  # skip this iteration to avoid adding to current_width
        if character.isspace():
            # a whitespace character, we can safely break here
            # index + 1 because we want the space to be at the end of the part
            # this way we can remove it with rstrip
            last_whitespace_index = index + 1
        # for anything but a newline, add +1 to current_width
        current_width += 1
    return splits


whitespace_checker = re.compile(r"\n\s*$")
"""Checks if the string ends with a newline followed by optional whitespaces."""


class RawDescriptionPreservedHelpRichHelpFormatter(rich_argparse.RawTextRichHelpFormatter):
    """Rich help message formatter which retains any formatting in descriptions.
    In argument help, it preserves new lines and still wrap the text to the available width, with proper indentation.
    """

    def _rich_split_lines(self, text: Text, width: int) -> Lines:
        if len(text) < width:
            return text.split()
        splits = split_formatted_text(text, width)
        splitted = text.divide(splits)
        for x in splitted:
            # remove all whitespace that divide had to preserve
            x.rstrip()
        return splitted


class RawDescriptionNewLineDefaultRichHelpFormatter(rich_argparse.RawTextRichHelpFormatter):
    """Rich help message formatter which retains any formatting in descriptions.
    Prints default values for arguments on a new line after the help message.
    """

    def _get_help_string(self, action):
        """
        Add the default value to the option help message.

        ArgumentDefaultsHelpFormatter and BooleanOptionalAction when it isn't
        already present. This code will do that, detecting cornercases to
        prevent duplicates or cases where it wouldn't make sense to the end
        user.
        """
        help_str = action.help
        if help_str is None:
            help_str = ""

        if "%(default)" not in help_str:
            if action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if whitespace_checker.match(help_str):
                        help_str += "(default: %(default)s)"
                    else:
                        help_str += "\n(default: %(default)s)"
        return help_str


class RawDescriptionPreservedHelpNewLineDefaultRichHelpFormatter(
    RawDescriptionPreservedHelpRichHelpFormatter, RawDescriptionNewLineDefaultRichHelpFormatter
):
    """Rich help message formatter which retains any formatting in descriptions.
    In argument help, it preserves new lines and still wrap the text to the available width, with proper indentation.
    Prints default values for arguments on a new line after the help message.
    """

    def _rich_split_lines(self, text: Text, width: int) -> Lines:
        if len(text) < width:
            return text.split()
        splits = split_formatted_text(text, width)
        splitted = text.divide(splits)
        for x in splitted:
            # remove all whitespace that divide had to preserve
            x.rstrip()
        return splitted

    def _get_help_string(self, action):
        """
        Add the default value to the option help message.

        ArgumentDefaultsHelpFormatter and BooleanOptionalAction when it isn't
        already present. This code will do that, detecting cornercases to
        prevent duplicates or cases where it wouldn't make sense to the end
        user.
        """
        help_str = action.help
        if help_str is None:
            help_str = ""

        if "%(default)" not in help_str:
            if action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if whitespace_checker.match(help_str):
                        help_str += "(default: %(default)s)"
                    else:
                        help_str += "\n(default: %(default)s)"
        return help_str
