from pathlib import Path
import json

import tqdm

_QUIET: bool = False
_WRITER: tqdm.tqdm | None = None

_ENGLISH_LOCALIZATION: dict[str, str] = {
    "FilesToProcess": """
╔════════════════╗
║ Files To Merge ║
╠════════════════╝
║""",
    "OutputSaved": "Saved in '{0}'.",
    "UnknownFileType": "Unknown file type {0}.",
    "MergedFile": "Merged: '{0}'.",
    "Merging": "Merging... ({0} pages)",
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
    global _WRITER
    _WRITER = writer


def get_writer():
    return _WRITER


def set_quiet(is_quiet: bool):
    # pylint: disable=global-statement
    global _QUIET
    _QUIET = bool(is_quiet)


def get_quiet():
    return _QUIET


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


def log(msg_key: str, *args, **kwargs):
    if _QUIET:
        return None
    message = CURRENT_LOCALIZATION.get(msg_key, _ENGLISH_LOCALIZATION[msg_key])
    try:
        return message.format(*args, **kwargs)
    except (IndexError, KeyError):
        return _ENGLISH_LOCALIZATION[msg_key].format(*args, **kwargs)


def _print(s):
    if _QUIET:
        return
    if _WRITER:
        _WRITER.write(str(s))
    else:
        print(s)


def printline():
    _print("")


def printlog(msg_key: str, *args, **kwargs):
    log_or_not = log(msg_key, *args, **kwargs)
    if log_or_not:
        _print(log_or_not)
