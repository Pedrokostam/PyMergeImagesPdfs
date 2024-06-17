from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Sequence
from tomlkit import comment, document, nl, item, dump, load
import pymupdf
from .dimension import Dimension


def expand_path(path: str | Path):
    str_path = os.path.expandvars(str(path))
    str_path = os.path.expanduser(str_path)
    return str_path


@dataclass
class Config:
    _output_folder: str = '.'
    _libreoffice_path: list[str] = field(
        default_factory=lambda: [
            r"%PROGRAMFILES(X86)%\LibreOffice\program\soffice.exe",
            r"%PROGRAMFILES%\LibreOffice\program\soffice.exe",
        ]
    )

    _margin: str | Dimension = "0x0"
    _page_size: str | Dimension = "A4"

    @property
    def margin(self):
        if isinstance(self._margin, Dimension):
            return self._margin
        if isinstance(self._margin, str):
            return Dimension.from_str(self._margin)
        raise ValueError()

    @property
    def libreoffice_path(self):
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

    def output_folder_expanded(self, base_path: Path):
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
        self._output_folder = str(value or '.')

    def save_config(self, destination: str | Path):
        d = document()
        d.add(comment("Configuration file for stitcher"))
        d.add(nl())
        d.add(comment("Path to Libre Office executable. Multiple paths can be specified, first valid will be used."))
        d.add(comment("If no path is valid or none exists, conversion of document formats is disabled."))
        d.add("libreoffice_path", item(self._libreoffice_path))
        d.add(nl())
        d.add(
            comment(
                "Path to the output folder. May contain '~' and variables (% and $). "
                "If not specified, current working directory will be used."
            )
        )
        d.add("output_folder", item(self._output_folder))
        d.add(nl())
        d.add(comment("Margin to be used when adding images. Horizontal then vertical dimension, separated by 'x'"))
        d.add("margin", item(str(self.margin)))
        d.add(nl())
        d.add(comment("Page size to be used when adding images. Horizontal then vertical dimension, separated by 'x'."))
        d.add(comment("Can also specify common paper sizes, like 'A4'"))
        d.add("page_size", item(str(self.page_size)))
        with open(str(destination), "w") as fp:
            dump(d, fp)

    def update(self, path: str):
        with open(path, "r") as fp:
            doc = load(fp)
            self.margin = doc.get("margin")
            self.page_size = doc.get("page_size")
            self.output_folder = doc.get("output_folder")
            self.libreoffice_path = doc.get("libreoffice_path")
