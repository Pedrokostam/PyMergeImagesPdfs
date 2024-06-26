import re
from typing import Sequence
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


def cm_to_points(cm_tuple: tuple[float, float]):
    return (cm_tuple[0] / 2.54 * 72, cm_tuple[1] / 2.54 * 72)


class Dimension:
    def __init__(self, horizontal: float, vertical: float | None, unit: str) -> None:
        unit = unit.casefold().strip()
        if unit == "mm":
            unit_mult = PT_BY_MM
        elif unit == "cm":
            unit_mult = PT_BY_CM
        elif unit in ["inch", '"']:
            unit_mult = PT_BY_INCH
        elif unit in ["pt", ""]:
            unit_mult = 1
        else:
            raise ValueError(f"Invalid unit type {unit}")
        self.horizontal = horizontal * unit_mult
        self.vertical = (vertical or horizontal) * unit_mult

    @property
    def rect(self) -> pymupdf.Rect:
        return pymupdf.Rect(x0=0, y0=0, x1=self.horizontal, y1=self.vertical)

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

    def __sub__(self, other: "Dimension | pymupdf.Rect") -> "Dimension":
        d = _try_to_convert_to_dimension(other)
        return Dimension(self.horizontal - d.horizontal, self.vertical - d.vertical, "pt")

    def __rsub__(self, other: "Dimension | pymupdf.Rect") -> "Dimension":
        d = _try_to_convert_to_dimension(other)
        return Dimension(d.horizontal - self.horizontal, d.vertical - self.vertical, "pt")

    def __add__(self, other: "Dimension | pymupdf.Rect") -> "Dimension":
        d = _try_to_convert_to_dimension(other)
        return Dimension(self.horizontal + d.horizontal, self.vertical + d.vertical, "pt")

    def __radd__(self, other: "Dimension | pymupdf.Rect") -> "Dimension":
        d = _try_to_convert_to_dimension(other)
        return Dimension(d.horizontal + self.horizontal, d.vertical + self.vertical, "pt")

    def __neg__(self):
        return Dimension(-self.horizontal, -self.vertical, "pt")

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

    def __str__(self):
        return self.to_unit_str("cm")

    def to_unit_str(self, unit: str | None = None):
        values = (self.horizontal, self.vertical)
        if unit:
            unit = unit.casefold().strip()
            if unit == "cm":
                values = [x / PT_BY_CM for x in values]
            elif unit == "mm":
                values = [x / PT_BY_MM for x in values]
            elif unit in ["inch", '"']:
                values = [x / PT_BY_INCH for x in values]
            elif unit in ["pt", ""]:
                unit = "pt"
            else:
                raise ValueError(f"Invalid unit type {unit}")
        unit = unit or "pt"
        return f"{values[0]:.2f}{unit} x {values[1]:.2f}{unit}"


def _try_to_convert_to_dimension(o):
    if isinstance(o, Dimension):
        return o
    if isinstance(o, Sequence):
        if len(o) == 2:
            return Dimension(o[0], o[1], "pt")
        if len(o) > 3:
            return Dimension(o[3], o[4], "pt")
        raise ValueError(f"Cannot {o} convert to Dimension")
    if isinstance(o, pymupdf.Rect):
        return Dimension(o.width, o.height, "pt")
    raise ValueError(f"Cannot {o} convert to Dimension")
