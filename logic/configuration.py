import json
from pathlib import Path
import sys

import click
import logic.languages as languages
import os


TRANSLATION: languages.Language = languages.en

OUTPUT_PATH_STR = "."
OUTPUT_PATH = Path(OUTPUT_PATH_STR)

IMAGE_PAGE_SIZE_STR = "a4"


def get_text() -> languages.Language:
    return TRANSLATION


def set_page_size(size_str: str):
    global IMAGE_PAGE_SIZE_STR
    IMAGE_PAGE_SIZE_STR = size_str  # type: ignore


def get_page_size() -> str:
    return IMAGE_PAGE_SIZE_STR


def get_lang_id() -> str:
    return TRANSLATION.id


def get_output_path() -> Path:
    return OUTPUT_PATH


def get_output_path_str() -> str:
    return OUTPUT_PATH_STR


def set_output_path(path: str):
    global OUTPUT_PATH_STR
    global OUTPUT_PATH
    OUTPUT_PATH_STR = Path(path)  # type: ignore
    str_path = os.path.expandvars(path)
    str_path = os.path.expanduser(str_path)
    str_path = os.path.expanduser(str_path)
    OUTPUT_PATH = Path(str_path)  # type: ignore


def set_language(id: str):
    global TRANSLATION
    lang = getattr(languages, id, TRANSLATION)
    TRANSLATION = lang  # type: ignore


def load_config(folder: Path):
    config_path = list(folder.glob("config.json"))
    if not config_path:
        click.echo("No config file")
    else:
        try:
            with open(config_path[0], mode="r") as config_handle:
                configuration_dict = json.load(config_handle)
                str_path = configuration_dict.get("output_path", ".")
                set_output_path(str_path)
                language = configuration_dict.get("language", "en")
                set_language(language)
                page_size_str = configuration_dict.get("image_page_size", "a4")
                set_page_size(page_size_str)
        except json.decoder.JSONDecodeError:
            click.echo("Invalid config file!", err=True)


def save_config(folder: Path):
    program_folder = Path(globals().get("__file__", sys.argv[0])).parent
    config_path = program_folder.joinpath("config.json")
    with open(config_path, "w") as save_handle:
        config_dict = {"output_path": OUTPUT_PATH_STR, "language": TRANSLATION.id}
        json.dump(config_dict, save_handle, indent=3)
        click.echo(get_text().msg_config_saved + str(OUTPUT_PATH_STR))
        click.echo(config_dict)
