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
        self._original_text = ""

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
        p_size = pymupdf.paper_size(text)
        if p_size != (-1, -1):
            dim = Dimension(p_size[0], p_size[1], "pt")
            dim._original_text = text
            return dim

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
        dim._original_text = text
        return dim

    def __str__(self):
        return self.to_unit_str(None)

    def to_unit_str(self, unit: str | None = None):
        values = (self.horizontal, self.vertical)
        if not unit and self._original_text:
            return self._original_text
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
    margin: Dimension = Dimension(0, 0, "pt")
    page_size: Dimension = Dimension.from_str("A4")

    @property
    def output_folder_expanded(self):
        return Path(expand_path(self._output_folder))

    def save_config(self, destination: str | Path):
        doc = document()
        doc.add(comment("Configuration file for stitcher"))

        doc.add(nl())
        doc.add(comment("Path to the output folder. May contain '~'."))
        doc.add("output_folder", item(str(self._output_folder)))

        doc.add(nl())
        doc.add(comment("Margin to be used when adding images. Horizontal then vertical dimension, separated by 'x'"))
        doc.add("margin", item(str(self.margin)))

        doc.add(nl())
        doc.add(
            comment("Page size to be used when adding images. Horizontal then vertical dimension, separated by 'x'.")
        )
        doc.add(comment("Can also specify common paper sizes, like 'A4'"))
        doc.add("page_size", item(str(self.page_size)))

        with open(str(destination), "w") as fp:
            dump(doc, fp)

    def update(self, path: str):
        with open(path, "r") as fp:
            doc = load(fp)
            if m := doc.get("margin"):
                self.margin = Dimension.from_str(m)
            if p := doc.get("page_size"):
                self.page_size = Dimension.from_str(p)
            if o := doc.get("output_folder"):
                self._output_folder = o
