from dataclasses import dataclass
import os
from pathlib import Path
from tomlkit import comment, document, nl, item, dump, load
import pymupdf
from .dimension import Dimension


def expand_path(path: str | Path):
    str_path = os.path.expandvars(str(path))
    str_path = os.path.expanduser(str_path)
    return str_path


@dataclass
class Config:
    _output_folder: str = "~"
    _libreoffice_path: str = r"%PROGRAMFILES(X86)%\LibreOffice\program\soffice.exe"

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
        p = Path(expand_path(self._libreoffice_path))
        if not p.exists:
            return None
        return p.absolute()

    @libreoffice_path.setter
    def libreoffice_path(self, path: str | Path | None):
        if path:
            self._libreoffice_path = str(path)

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
        expanded = Path(expand_path(self._output_folder))
        if not expanded.is_absolute():
            return base_path.joinpath(expanded)
        return expanded

    @property
    def output_folder(self):
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: str | Path | None):
        if value:
            self._output_folder = str(value)

    def save_config(self, destination: str | Path):
        d = document()
        d.add(comment("Configuration file for stitcher"))
        d.add(nl())
        d.add(comment("Path to Libre Office executable"))
        d.add(comment("If the path is not valid or does not exists, conversion of LibreOffice formats is disabled."))
        d.add("libreoffice_path", item(self._libreoffice_path))
        d.add(comment("Path to the output folder. May contain '~' and $ variables."))
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
