import re
import sys
import json
from pathlib import Path
from cx_Freeze import setup, Executable
from implementation.logger import _ENGLISH_LOCALIZATION

# Dependencies are automatically detected, but it might need
# fine tuning.


sys.excepthook = lambda et, e, t: print("%s: %s" % (et.__name__, e))

SETUP_ROOT = Path(__file__).parent


class InvalidIndentifierError(ValueError):
    pass


class MissingRequiredIdentifierError(ValueError):
    pass


class MismatchedPlaceholdersError(ValueError):
    pass


class RedundantIdentifierError(ValueError):
    pass


def check_logger():
    py_files = list(SETUP_ROOT.glob("*.py"))
    py_files += SETUP_ROOT.joinpath("implementation").glob("*.py")
    keys = set(_ENGLISH_LOCALIZATION.keys())
    for py_file in py_files:
        with open(py_file, "r", encoding="utf8") as python_script_file:
            script = python_script_file.readlines()
            for line_number, line in enumerate(script):
                find_unknown_identifiers(keys, py_file, line_number, line)


def find_unknown_identifiers(keys, py_file, line_number, line):
    path = py_file.relative_to(SETUP_ROOT)
    matches = re.findall(r"""translated?\(\s*["'](?P<identifier>\w+)["']""", line)
    for match in matches:
        if match not in keys:
            raise InvalidIndentifierError(
                f"File {path} contains unknown message identifier at line {line_number}: {match}"
            )


def update_language() -> list[str]:
    with open(SETUP_ROOT.joinpath("language.en.json"), "w", encoding="utf8") as foreign_lang_json:
        json.dump(_ENGLISH_LOCALIZATION, foreign_lang_json, indent=2)

    foreign_lang_files = list(SETUP_ROOT.glob("language.*.json"))
    for foreign_lang_file in foreign_lang_files:
        relative = foreign_lang_file.relative_to(SETUP_ROOT)
        with open(foreign_lang_file, "r", encoding="utf8") as foreign_lang_json:
            lang_dict: dict[str, str] = json.load(foreign_lang_json)
            for key, value in _ENGLISH_LOCALIZATION.items():
                if key not in lang_dict:
                    raise MissingRequiredIdentifierError(f"Localization dict {relative} does not have key {key}!")
                placeholder_target = set(re.findall("{[^}]+}", value))
                placeholder_actual = set(re.findall("{[^}]+}", lang_dict[key]))
                different_placeholders = placeholder_target.difference(placeholder_actual)
                # placeholder_count_target = len(re.findall("{.+}", value))
                # placeholder_count_actual = len(re.findall("{.+}", lang_dict[key]))
                if different_placeholders:
                    raise MismatchedPlaceholdersError(
                        f"Key {key} in {relative} has "
                        "different number of placeholders than the English version!"
                        f"(default has: {list(placeholder_target)}; "
                        f"{foreign_lang_file.stem} has: {list(placeholder_actual)})"
                    )
            difference = set(lang_dict.keys()).difference(_ENGLISH_LOCALIZATION.keys())
            if difference:
                raise RedundantIdentifierError(
                    f"Language file {foreign_lang_file} has more keys than default: {difference}"
                )

    return [f.name for f in foreign_lang_files]


def get_from_requirements():
    with open(SETUP_ROOT.joinpath("requirements.txt"), "r", encoding="utf8") as req:
        modules = [x.split("=")[0].lower() for x in req.readlines()]
        modules = [m for m in modules if m != "cx_freeze"]
        return modules


check_logger()
lang_files = update_language()

build_options = {
    "packages": get_from_requirements(),
    "excludes": [],
    "include_files": [
        "config_dragdrop.toml",
    ]
    + lang_files,
}

base = "console"

executables = [Executable("merge_documents.py", base=base, icon="./icon.ico")]

setup(
    name="Document merger",
    version="2.0",
    description="Merges PDFs, images and document format (MicroSoft office and OpenDocument) into one PDF file.",
    options={"build_exe": build_options},
    executables=executables,
)
