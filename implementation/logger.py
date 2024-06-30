from os import get_terminal_size
from pathlib import Path
from typing import Any
import json

import tqdm

__QUIET: bool = False
__WRITER: tqdm.tqdm | None = None


_ENGLISH_LOCALIZATION: dict[str, str] = {
    "FilesToProcess": """
╔════════════════╗
║ Files To Merge ║
╠════════════════╝
║""",
    "OutputSaved": "Saved in '{0}'.",
    "UnknownFileType": "Unknown file type {0}.",
    "MergedFile": "Merged: '{0}'.",
    "Merging": "Merging... (page count: {0})",
    "MergingFinished": "Merged (page count: {0}).",
    "EnumeratingInput": "Enumerating files...",
    "FirstPageSize": "First PDF page size: {0}.",
    "GeneratedDefaultConfig": "Generated default configration file.",
    "ConfigNotFound": "Configuration file '{0}' not found. Aborting...",
    "ConfigSaved": "Configuration saved to '{0}'",
    "LibreMissing": "Attempted to merge a document file, but LibreOffice is not installed. File '{0}' is ignored.",
    "ConfirmExit": "Press ENTER to exit...",
    "InputSorted": "Sorted all input paths alphabetically.",
    "WhatIfMode": 'Program was run in "What if?" mode. No output PDF was created.',
    "NoFilesToProcess": "No supported files to merge. Aborting...",
}

CURRENT_LOCALIZATION: dict[str, str] = _ENGLISH_LOCALIZATION


def set_writer(writer: tqdm.tqdm | None):
    # pylint: disable=global-statement
    global __WRITER
    __WRITER = writer


def get_writer():
    return __WRITER


def set_quiet(is_quiet: bool):
    # pylint: disable=global-statement
    global __QUIET
    __QUIET = bool(is_quiet)


def get_quiet():
    return __QUIET


def set_language_from_file(path: Path, identifier: str | None):
    pattern = f".{identifier}" if identifier else "*"
    lang_files = sorted(path.glob(f"language{pattern}.json"))
    # pylint: disable=global-statement
    global CURRENT_LOCALIZATION
    for lang_file in lang_files:
        if lang_file.exists():
            with open(lang_file, "r", encoding="utf8") as f:
                CURRENT_LOCALIZATION = json.load(f)
                return


def translate(msg_key: str, *args, **kwargs):
    """Finds the message in current localization by msk_key and returns it, formatted with given args and kwargs.

    If the message is not in the localization, or has too many placeholders
    returns the message from the default localization.

    If that is missing as well, raise a KeyError.

    Args:
        msg_key (str): Key of the message in the localization file.

    Returns:
        _type_: Formatted localized string
    """
    default_value = _ENGLISH_LOCALIZATION[msg_key]
    message = CURRENT_LOCALIZATION.get(msg_key, default_value)
    try:
        return message.format(*args, **kwargs)
    except (IndexError, KeyError):
        return default_value.format(*args, **kwargs)


def print_message(s: Any, overprint: bool = False):
    """
    Prints the given message.

    If --quiet is True, does nothing.

    If a progress bar is active, redirects the message to bar.write().

    Args:
        s (Any): Objects, whose result of __str__ will be printed.
    """
    if __QUIET:
        return
    msg = str(s)
    end = "\n"
    if overprint:
        to_fill = get_terminal_size().columns - len(msg)
        msg += " " * (to_fill-1)
        end = "\r"
    if __WRITER:
        __WRITER.write(msg, end=end)
    else:
        print(msg, end=end)


def print_newline():
    """
    Call print_message with an empty string, resulting in an empty line being printed.

    If --quiet is True, does nothing.
    """
    print_message("")


def print_translated(msg_key: str, *args, overprint: bool = False, **kwargs):
    log = translate(msg_key, *args, **kwargs)
    if log:
        print_message(log, overprint=overprint)
