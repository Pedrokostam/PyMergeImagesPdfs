import re
import json
from pathlib import Path
from cx_Freeze import setup, Executable
from implementation.logger import _ENGLISH_LOCALIZATION

# Dependencies are automatically detected, but it might need
# fine tuning.

SETUP_ROOT = Path(__file__).parent


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
                    raise ValueError(f"Localization dict {relative} does not have key {key}!")
                placeholder_count_target = len(re.findall("{.+}", value))
                placeholder_count_actual = len(re.findall("{.+}", lang_dict[key]))
                if placeholder_count_target != placeholder_count_actual:
                    raise ValueError(
                        f"Key {key} in {relative} has "
                        "different number of placeholders than the English version!"
                        f"({lang_dict[key]} vs. {value})"
                    )
    return [f.name for f in foreign_lang_files]


def get_from_requirements():
    with open(SETUP_ROOT.joinpath("requirements.txt"), "r", encoding="utf8") as req:
        modules = [x.split("=")[0].lower() for x in req.readlines()]
        return modules


lang_files = update_language()

build_options = {
    "packages": get_from_requirements(),
    "excludes": [],
    "include_files": [
        "config_dragdrop (change name to config to make default).toml",
        "language.json",
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
