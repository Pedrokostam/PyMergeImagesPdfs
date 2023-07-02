from pathlib import Path
from typing import Sequence

EXTENSIONS: list[str] = [x.casefold() for x in [".pdf", ".png", ".jpg", ".bmp", ".jpeg", '.tif','.tiff']]


def get_files(paths: Sequence[Path]) -> list[Path]:
    """Recursively list files and directories up to a certain depth"""
    paths = [Path(p) for p in paths]
    files: list[Path] = []
    for p in paths:
        if p.is_file() and match_suffix(p):
            files.append(p)
        elif p.is_dir():
            gen = p.rglob("*.*")
            for f in gen:
                if f.is_file() and match_suffix(f):
                    files.append(f)
    return files


def match_suffix(path: Path) -> bool:
    return path.suffix.casefold() in EXTENSIONS
