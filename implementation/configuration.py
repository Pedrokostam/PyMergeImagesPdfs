from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Sequence
from tomlkit import TOMLDocument, comment, document, nl, item, dump, load, register_encoder
import pymupdf
from .logger import printlog
from .dimension import Dimension

# register fallback string encoder. Dimension can be parsed to and from string
register_encoder(lambda x: item(str(x)))

PATH_DISCLAIMER = [
    "Paths may contain '~' and environmental variables (surrounded with '%%' or prepended with '$').",
    "You can use both forward and backward slashes. Backward slashes need to be doubled."
    "Can be relative (to the current working directory).",
]


UNIT_DICLAIMER = " \n".join(
    [
        'Format: "(width)(unit) x (height)(unit)". Units have to match.',
        "You can use points (pt), millimetres (m), centimetres (cm) and inches (inch) as units. "
        "Default unit is point.",
    ]
)

LIBREOFFICE_PATH_DESCRIPTION = " \n".join(
    [
        "Path to Libre Office executable.",
        "First available path will be used.",
        "If no path is valid conversion of document formats is disabled.",
    ]
    + PATH_DISCLAIMER
)

MARGIN_DESCRIPTION: str = " \n".join(
    [
        "Margin to be used when adding images.",
        UNIT_DICLAIMER,
    ]
)

IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION: str = " \n".join(
    [
        "When adding images, the page size is set to first PDF's first page size.",
        "If there are no PDF files provided, the fallback value is used.",
        UNIT_DICLAIMER,
        "Can also specify common paper sizes, like 'A4'.",
    ]
)

FORCE_IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION: str = " \n".join(
    [
        "If True, the specified fallback size will always be used for image pages, regardless of other PDF files.",
    ]
)

ALPHABETIC_FILE_SORTING_DESCRIPTION = " \n".join(
    [
        "When true the order in which the paths are specified is ignored - "
        "all paths are sorted alphabetically as if they were in one directory.",
        "Useful when using the program by dragging the files onto the executable.",
    ]
)

LANGUAGE_DESCRIPTION = " \n".join(
    [
        "Which language file to load. Language files should follow "
        "the 'language.[lang].json' pattern where 'lang' is an identifier for the language.",
        "This argument accepts this identifier. ",
        "If the identifier is an empty string, first available file is loaded.",
        "If the matching file is not found, default language will be used.",
    ]
)

CONFIRM_EXIT_DESCRIPTION = "If True, will not exit the program until user confirms."

QUIET_DESCRIPTION = "If True, prints no messages to the console. Overrides --confirm-exit."


RECURSION_DESCRIPTION = "How deep to search for supported files in a directory."


def expand_path(path: str | Path):
    str_path = os.path.expandvars(str(path))
    str_path = os.path.expanduser(str_path)
    return str_path


def add_comment(doc: TOMLDocument, item_comment):
    doc.add(comment(str(item_comment)))


def newline(doc: TOMLDocument):
    doc.add(nl())


@dataclass
class Configuration:
    # pylint: disable=too-many-instance-attributes
    _output_directory: str = "."
    _libreoffice_path: list[str] = field(
        default_factory=lambda: [
            r"%PROGRAMFILES%\LibreOffice\program\soffice.exe",
            r"%PROGRAMFILES(X86)%\LibreOffice\program\soffice.exe",
        ]
    )

    _margin: str | Dimension = "0mm x 0mm"
    _image_page_fallback_size: str | Dimension = "A4"
    force_image_page_fallback_size: bool = False
    alphabetic_file_sorting: bool = False
    confirm_exit: bool = False
    quiet: bool = False
    recursion_limit: int = 5
    whatif: bool = False
    language: str = ""

    def add_item(self, doc: TOMLDocument, key: str, description: list[str] | str):
        newline(doc)
        if isinstance(description, list):
            description = "\n".join(description)
        description = description.split("\n")
        for desc_line in description:
            add_comment(doc, desc_line)
        value = getattr(self, key)
        default_value = item(value).as_string()
        add_comment(doc, f"Default value: {default_value}")
        dict_key = key if not key.startswith("_") else key[1:]
        doc.add(dict_key, item(value))

    def _set_not_None(self, var_name: str, value):
        if value is not None:
            setattr(self, var_name, value)

    def _set_from_dictlike(self, var_name: str, dictlike: dict | TOMLDocument):
        """
        Finds value by key in the dictlike and tries to set the property of the same to that value,
        If dictlike does not have this key, does nothing.
        If var_name is prepended with '_' the underscored is ignored for dictlike, but preserved for setattrr
        """
        dict_name = var_name[1:] if var_name.startswith("_") else var_name
        self._set_not_None(var_name, dictlike.get(dict_name, None))

    @property
    def margin(self) -> Dimension:
        if isinstance(self._margin, Dimension):
            return self._margin
        if isinstance(self._margin, str):
            return Dimension.from_str(self._margin)
        raise ValueError()

    @margin.setter
    def margin(self, value: str | Dimension | None):
        if value:
            self._margin = value

    @property
    def image_page_fallback_size(self):
        if isinstance(self._image_page_fallback_size, Dimension):
            return self._image_page_fallback_size
        if isinstance(self._image_page_fallback_size, str):
            p_size = pymupdf.paper_size(self._image_page_fallback_size)
            if p_size != (-1, -1):
                return Dimension(p_size[0], p_size[1], "pt")
            return Dimension.from_str(self._image_page_fallback_size)
        raise ValueError()

    @image_page_fallback_size.setter
    def image_page_fallback_size(self, value: str | Dimension | None):
        if value:
            self._image_page_fallback_size = value

    @property
    def libreoffice_path(self) -> Path | None:
        """Checks if LibreOffice executable exists and returns its path.

        Returns:
            pathlib.Path | None: Path if libreoffice executable exists at this location, None otherwise
        """
        for path in self._libreoffice_path:
            expanded_path = Path(expand_path(path))
            if expanded_path.exists():
                return expanded_path.absolute()
        return None

    @libreoffice_path.setter
    def libreoffice_path(self, path: Sequence[str] | Sequence[Path] | None):
        if path:
            self._libreoffice_path = [str(x) for x in path]

    def output_directory_expanded(self, base_path: Path) -> Path:
        if not self._output_directory:
            return base_path
        expanded = Path(expand_path(self._output_directory))
        if not expanded.is_absolute():
            return base_path.joinpath(expanded)
        return expanded

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value: str | Path | None):
        if value:
            self._output_directory = str(value)

    def save_config(self, destination: str | Path):
        doc = document()
        add_comment(doc, "Configuration file for stitcher")

        self.add_item(
            doc,
            "_libreoffice_path",
            LIBREOFFICE_PATH_DESCRIPTION,
        )
        self.add_item(doc, "language", LANGUAGE_DESCRIPTION)
        self.add_item(doc, "_output_directory", ["Path to the output folder."] + PATH_DISCLAIMER)
        self.add_item(doc, "_margin", MARGIN_DESCRIPTION)
        self.add_item(doc, "_image_page_fallback_size", IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION)
        self.add_item(
            doc,
            "force_image_page_fallback_size",
            FORCE_IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION,
        )
        self.add_item(doc, "alphabetic_file_sorting", ALPHABETIC_FILE_SORTING_DESCRIPTION)
        self.add_item(doc, "confirm_exit", CONFIRM_EXIT_DESCRIPTION)
        self.add_item(doc, "quiet", QUIET_DESCRIPTION)
        self.add_item(doc, "recursion_limit", RECURSION_DESCRIPTION)
        with open(str(destination), "w", encoding="utf8") as fp:
            dump(doc, fp)
        printlog("ConfigSaved", destination)

    def update_from_toml(self, path: Path | str):
        """Opens specified TOML file and updates the properites of this instance with the values from TOML.
        Keys that are not specified in the file are unchanged.

        Args:
            path (Path | str): Path to the TOML file.
        """
        with open(path, "r", encoding="utf8") as fp:
            doc = load(fp)
            self.update_from_dictlike(doc)

    def update_from_dictlike(self, dictionary: dict | TOMLDocument):
        self._set_from_dictlike("_margin", dictionary)
        self._set_from_dictlike("_image_page_fallback_size", dictionary)
        self._set_from_dictlike("force_image_page_fallback_size", dictionary)
        self._set_from_dictlike("output_directory", dictionary)
        self._set_from_dictlike("libreoffice_path", dictionary)
        self._set_from_dictlike("alphabetic_file_sorting", dictionary)
        self._set_from_dictlike("confirm_exit", dictionary)
        self._set_from_dictlike("quiet", dictionary)
        self._set_from_dictlike("recursion_limit", dictionary)
        self._set_from_dictlike("language", dictionary)
        if isinstance(dictionary, dict):
            # whatif should not be read from TOML
            self._set_from_dictlike("whatif", dictionary)
