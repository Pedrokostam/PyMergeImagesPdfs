from string import Template
from typing import Sequence


DEFAULT_DICT: dict[str, str] = {
    "tln_config_saved": "Configuration file saved: $path",
    "tln_merged_prefix": "merged_$date.pdf",
}
DEFAULT_DICT_PL: dict[str, str] = {
    "tln_config_saved": "Plik konfiguracyjny zapisany: $path",
}


class Translator:
    def set_locale(self, loc: str):
        self.current_dict = self.dicts.get(loc, self.current_dict)

    def __init__(self) -> None:
        self.dicts = {"en": DEFAULT_DICT, "pl": DEFAULT_DICT_PL}
        self.current_dict = self.dicts["en"]

    def translate_impl(self, template: str, **kwargs: Sequence[str]):
        return Template(template).safe_substitute(**kwargs)

    def get(self, key: str, **kwargs: Sequence[str]):
        template = self.current_dict.get(key, DEFAULT_DICT[key])
        return self.translate_impl(template, **kwargs)


TRANSLATOR = Translator()
