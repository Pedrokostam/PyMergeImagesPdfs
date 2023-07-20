import glob
from pathlib import Path
from typing import Sequence

from natsort import os_sorted

EXTENSIONS: list[str] = [
    x.casefold()
    for x in [
        ".pdf",
        ".png",
        ".jpg",
        ".bmp",
        ".jpeg",
    ]
]


def is_image(path: Path):
    return path.suffix.casefold() != '.pdf'


def get_files_single(path: str) -> list[Path]:
    """Recursively list files and directories up to a certain depth"""
    p = [Path(x) for x in glob.glob(path)]
    return get_files(p)


def get_files(paths: Sequence[Path]) -> list[Path]:
    """Recursively list files and directories up to a certain depth"""
    paths = [Path(p) for p in paths]
    files: list[Path] = []
    for p in paths:
        if p.is_file() and match_suffix(p):
            files.append(p)
        elif p.is_dir():
            gen: list[Path] = os_sorted(p.rglob("*.*"))
            for f in gen:
                if f.is_file() and match_suffix(f):
                    files.append(f)
    return files


def match_suffix(path: Path) -> bool:
    return path.suffix.casefold() in EXTENSIONS
