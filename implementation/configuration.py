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

path_disclaimer = [
    "Paths may contain '~' and environmental variables (surrounded with '%' or prepended with '$').",
    "You can use both forward and backward slashes. Backward slashes need to be doubled."
    "Can be relative (to the current working directory).",
]


unit_disclaimer = " \n".join(
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
    + path_disclaimer
)

MARGIN_DESCRIPTION: str = " \n".join(
    [
        "Margin to be used when adding images.",
        unit_disclaimer,
    ]
)

IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION: str = " \n".join(
    [
        "When adding images, the page size is set to first PDF's first page size.",
        "If there are no PDF files provided, the fallback value is used.",
        unit_disclaimer,
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
        "all paths are sorted as if they were in one directory.",
    ]
)

CONFIRM_EXIT_DESCRIPTION = "If True, will not exit the program until user confirms."

QUIET_DESCRIPTION = "If True, prints no messages to the console. Overrides confirm-exit."


def expand_path(path: str | Path):
    str_path = os.path.expandvars(str(path))
    str_path = os.path.expanduser(str_path)
    return str_path


def add_comment(doc: TOMLDocument, item_comment):
    doc.add(comment(str(item_comment)))


def newline(doc: TOMLDocument):
    doc.add(nl())


def add_item(doc: TOMLDocument, value, key: str, description: list[str] | str):
    newline(doc)
    if isinstance(description, list):
        description = "\n".join(description)
    description = description.split("\n")
    for desc_line in description:
        add_comment(doc, desc_line)
    add_comment(doc, f"Default value: {item(value).as_string()}")
    doc.add(key, item(value))


@dataclass
class Configuration:
    _output_directory: str = "."
    _libreoffice_path: list[str] = field(
        default_factory=lambda: [
            r"%PROGRAMFILES%\\LibreOffice\\program\\soffice.exe",
            r"%PROGRAMFILES(X86)%\\LibreOffice\\program\\soffice.exe",
        ]
    )

    _margin: str | Dimension = "0mm x 0mm"
    _image_page_fallback_size: str | Dimension = "A4"
    _force_image_page_fallback_size: bool = False
    _alphabetic_file_sorting: bool = False
    _confirm_exit: bool = False
    _quiet: bool = False

    @property
    def confirm_exit(self) -> bool:
        return self._confirm_exit

    @confirm_exit.setter
    def confirm_exit(self, value):
        if value is not None:
            self._confirm_exit = bool(value)

    @property
    def quiet(self) -> bool:
        return self._quiet

    @quiet.setter
    def quiet(self, value):
        if value is not None:
            self._quiet = bool(value)

    @property
    def force_image_page_fallback_size(self) -> bool:
        return self._force_image_page_fallback_size

    @force_image_page_fallback_size.setter
    def force_image_page_fallback_size(self, value):
        if value is not None:
            self._force_image_page_fallback_size = bool(value)

    @property
    def alphabetic_file_sorting(self) -> bool:
        return self._alphabetic_file_sorting

    @alphabetic_file_sorting.setter
    def alphabetic_file_sorting(self, value):
        if value is not None:
            self._alphabetic_file_sorting = bool(value)

    @property
    def margin(self) -> Dimension:
        if isinstance(self._margin, Dimension):
            return self._margin
        if isinstance(self._margin, str):
            return Dimension.from_str(self._margin)
        raise ValueError()

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

    @margin.setter
    def margin(self, value: str | Dimension | None):
        if value:
            self._margin = value

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

        add_item(
            doc,
            self._libreoffice_path,
            "libreoffice_path",
            LIBREOFFICE_PATH_DESCRIPTION,
        )
        add_item(doc, self._output_directory, "output_directory", ["Path to the output folder."] + path_disclaimer)

        add_item(doc, self._margin, "margin", MARGIN_DESCRIPTION)
        add_item(doc, self._image_page_fallback_size, "image_page_fallback_size", IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION)
        add_item(
            doc,
            self.force_image_page_fallback_size,
            "force_image_page_fallback_size",
            FORCE_IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION,
        )
        add_item(doc, self.alphabetic_file_sorting, "override_argument_order", ALPHABETIC_FILE_SORTING_DESCRIPTION)
        add_item(doc, self.confirm_exit, "confirm_exit", CONFIRM_EXIT_DESCRIPTION)
        add_item(doc, self.quiet, "quiet", QUIET_DESCRIPTION)
        with open(str(destination), "w") as fp:
            dump(doc, fp)
        printlog("ConfigSaved", destination)

    def update_from_toml(self, path: Path | str):
        """Opens specified TOML file and updates the properites of this instance with the values from TOML.
        Keys that are not specified in the file are unchanged.

        Args:
            path (Path | str): Path to the TOML file.
        """
        with open(path, "r") as fp:
            doc = load(fp)
            self.update_from_dictlike(doc)

    def update_from_dictlike(self, dictionary: dict | TOMLDocument):
        self.margin = dictionary.get("margin")
        self.image_page_fallback_size = dictionary.get("image_page_fallback_size")
        self.force_image_page_fallback_size = dictionary.get("force_image_page_fallback_size")
        self.output_directory = dictionary.get("output_directory")
        self.libreoffice_path = dictionary.get("libreoffice_path")
        self.alphabetic_file_sorting = dictionary.get("alphabetic_file_sorting")
        self.confirm_exit = dictionary.get("confirm_exit")
        self.quiet = dictionary.get("quiet")
