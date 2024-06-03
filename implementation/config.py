from dataclasses import dataclass
import os
from pathlib import Path
import re
from tomlkit import comment, document, nl, item, dump, load
import pymupdf

PT_BY_INCH = 72
PT_BY_CM = PT_BY_INCH / 2.54
PT_BY_MM = PT_BY_INCH / 25.4


def get_value_unit(s: str):
    value_match = re.search(r"[\d\.,]+", s)
    if not value_match:
        raise ValueError(f"Could not parse dimension {s}")
    value = float(value_match.group(0).replace(",", "."))
    just_unit = s.replace(value_match.group(0), " ").strip()
    return (value, just_unit)


class Dimension:
    def __init__(self, horizontal: float, vertical: float | None, unit: str) -> None:
        unit = unit.casefold().strip()
        if unit == "mm":
            unit_mult = PT_BY_MM
        elif unit == "cm":
            unit_mult = PT_BY_CM
        elif unit == "inch" or unit == '"':
            unit_mult = PT_BY_INCH
        elif unit == "pt" or unit == "":
            unit_mult = 1
        else:
            raise ValueError(f"Invalid unit type {unit}")
        self.horizontal = horizontal * unit_mult
        self.vertical = (vertical or horizontal) * unit_mult

    @classmethod
    def from_tuples(cls, horizontal: tuple[float, str], vertical: tuple[float, str] | None):
        part_tuples = [horizontal, vertical] if vertical else [horizontal]
        if len(part_tuples) == 1:
            actual_value = part_tuples[0]
            dim = Dimension(actual_value[0], actual_value[0], actual_value[1])
        else:
            actual_value_x = part_tuples[0]
            actual_value_y = part_tuples[1]
            if actual_value_x[1] != actual_value_y[1]:
                raise ValueError(f"Cannot mix unit in Margin {part_tuples}")
            dim = Dimension(actual_value_x[0], actual_value_y[0], actual_value_x[1])
        return dim

    @classmethod
    def from_str(cls, text: str):
        text = text.casefold()
        parts = text.split("x")
        if len(parts) == 0:
            raise ValueError(f"Invalid margin string {text}")
        if len(parts) > 2:
            raise ValueError(f"Margin can have up to 2 parts ({text})")

        part_tuples = [get_value_unit(x) for x in parts]
        horizontal_tuple = part_tuples[0]
        vertical_tuple = part_tuples[1] if len(part_tuples) > 1 else None
        dim = cls.from_tuples(horizontal_tuple, vertical_tuple)
        return dim

    def __repr__(self):
        return self.to_unit_str(None)

    def to_unit_str(self, unit: str | None = None):
        values = (self.horizontal, self.vertical)
        if unit:
            unit = unit.casefold().strip()
            if unit == "cm":
                values = [x / PT_BY_CM for x in values]
            elif unit == "mm":
                values = [x / PT_BY_MM for x in values]
            elif unit == "inch" or unit == '"':
                values = [x / PT_BY_INCH for x in values]
            elif unit == "pt" or unit == "":
                unit = "pt"
                pass
            else:
                raise ValueError(f"Invalid unit type {unit}")
        unit = unit or "pt"
        return f"{values[0]}{unit} x {values[1]}{unit}"


def expand_path(path: str | Path):
    str_path = os.path.expandvars(str(path))
    str_path = os.path.expanduser(str_path)
    return str_path


@dataclass
class Config:
    _output_folder: str = "~"

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
        d.add(comment("Path to the output folder. May contain '~' and $ variables."))
        d.add("output_folder", item(str(self._output_folder)))
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
