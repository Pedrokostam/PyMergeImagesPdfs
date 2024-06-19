from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Sequence
from tomlkit import TOMLDocument, comment, document, nl, item, dump, load, register_encoder
import pymupdf
from .dimension import Dimension

# register fallback string encoder. Dimension can be parsed to and from string
register_encoder(lambda x: item(str(x)))


def expand_path(path: str | Path):
    str_path = os.path.expandvars(str(path))
    str_path = os.path.expanduser(str_path)
    return str_path


def add_comment(doc: TOMLDocument, item_comment):
    doc.add(comment(str(item_comment)))


def newline(doc: TOMLDocument):
    doc.add(nl())


def add_item(doc: TOMLDocument, value, key: str, description: list[str]):
    newline(doc)
    for desc_line in description:
        add_comment(doc, desc_line)
    add_comment(doc, f"Default value: {item(value).as_string()}")
    doc.add(key, item(value))


@dataclass
class Config:
    _output_folder: str = "."
    _libreoffice_path: list[str] = field(
        default_factory=lambda: [
            r"%PROGRAMFILES%/LibreOffice/program/soffice.exe",
            r"%PROGRAMFILES(X86)%/LibreOffice/program/soffice.exe",
        ]
    )

    _margin: str | Dimension = "0mm x 0mm"
    _page_size: str | Dimension = "A4"

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
    def page_size(self):
        if isinstance(self._page_size, Dimension):
            return self._page_size
        if isinstance(self._page_size, str):
            p_size = pymupdf.paper_size(self._page_size)
            if p_size != (-1, -1):
                return Dimension(p_size[0], p_size[1], "pt")
            return Dimension.from_str(self._page_size)
        raise ValueError()

    @page_size.setter
    def page_size(self, value: str | Dimension | None):
        if value:
            self._page_size = value

    @margin.setter
    def margin(self, value: str | Dimension | None):
        if value:
            self._margin = value

    def output_folder_expanded(self, base_path: Path) -> Path:
        if not self._output_folder:
            return base_path
        expanded = Path(expand_path(self._output_folder))
        if not expanded.is_absolute():
            return base_path.joinpath(expanded)
        return expanded

    @property
    def output_folder(self):
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: str | Path | None):
        self._output_folder = str(value or ".")

    def save_config(self, destination: str | Path):
        doc = document()
        add_comment(doc, "Configuration file for stitcher")
        path_disclaimer = [
            "Paths may contain '~' and environmental variables (surrounded with '%' or prepended with '$').",
            "Can be relative (to the current working directory).",
        ]
        add_item(
            doc,
            self._libreoffice_path,
            "libreoffice_path",
            [
                "Path to Libre Office executable.",
                "First available path will be used.",
                "If no path is valid conversion of document formats is disabled.",
            ]
            + path_disclaimer,
        )
        add_item(doc, self._output_folder, "output_folder", ["Path to the output folder."] + path_disclaimer)
        unit_disclaimer = (
            "You can use points (pt), millimetres (m), centimetres (cm) and inches (inch) as units. "
            "Points are used if no unit is specified."
        )
        add_item(
            doc,
            self._margin,
            "margin",
            [
                "Margin to be used when adding images. Horizontal then vertical dimension, separated by 'x'.",
                unit_disclaimer,
            ],
        )
        add_item(
            doc,
            self._page_size,
            "page_size",
            [
                "Page size to be used when adding images. Horizontal then vertical dimension, separated by 'x'.",
                unit_disclaimer,
                "Can also specify common paper sizes, like 'A4'.",
            ],
        )
        with open(str(destination), "w") as fp:
            dump(doc, fp)

    def update(self, path: Path | str):
        """Opens specified TOML file and updates the properites of this instance with the values from TOML.
        Keys that are not specified in the file are unchanged.

        Args:
            path (Path | str): Path to the TOML file.
        """
        with open(path, "r") as fp:
            doc = load(fp)
            self.margin = doc.get("margin")
            self.page_size = doc.get("page_size")
            self.output_folder = doc.get("output_folder")
            self.libreoffice_path = doc.get("libreoffice_path")
