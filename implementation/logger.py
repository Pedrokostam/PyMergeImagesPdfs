_QUIET: bool = False

_ENGLISH_LOCALIZATION: dict[str, str] = {
    "OutputSaved": "Saved in '{0}'.",
    "UnknownFileType": "Unknown file type {0}.",
    "Stitching": "Stitching '{0}'.",
    "FirstPageSize": "First PDF page size '{0}'.",
    "GeneratedDefaultConfig": "Generated default configration file.",
    "ConfigNotFound": "Configuration file '{0}' not found. Aborting...",
    "ConfigSaved": "Configuration saved to '{0}'",
    "FileSkipped": "File '{0}' skipped due to unknown extension.",
    "LibreMissing": "Attempted to merge a document file, but LibreOffice is not installed. File '{0}' is ignored.",
    "ConfirmExit": "Press ENTER to exit...",
}

CURRENT_LOCALIZATION: dict[str, str] = _ENGLISH_LOCALIZATION


def set_quiet(is_quiet: bool):
    global _QUIET
    _QUIET = bool(is_quiet or False)


def log(msg_key: str, *args, **kwargs):
    if _QUIET:
        return
    message = CURRENT_LOCALIZATION.get(msg_key, _ENGLISH_LOCALIZATION[msg_key])
    return message.format(*args, **kwargs)


def printlog(msg_key: str, *args, **kwargs):
    log_or_not = log(msg_key, *args, **kwargs)
    if log_or_not:
        print(log_or_not)
