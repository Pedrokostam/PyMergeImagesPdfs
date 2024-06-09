from pathlib import Path
from natsort import natsorted, ns
import datetime


def is_pdf_extension(path: Path):
    return path.suffix.casefold() == ".pdf"


def is_image_extension(path: Path):
    suffix = path.suffix.casefold()
    return suffix in [".jpeg", ".jpg", ".tiff", ".png"]


def recurse_files(paths: list[str]):
    files_to_process: list[Path] = []
    for path in paths:
        pathpath = Path(path)
        if pathpath.is_dir():
            subfiles: list[Path] = []
            for f in pathpath.glob("**/*"):
                if is_image_extension(f) or is_pdf_extension(f):
                    subfiles.append(f)
            subfiles = natsorted(subfiles, alg=ns.IGNORECASE)
            files_to_process.extend(subfiles)
        else:
            files_to_process.append(pathpath)
    return files_to_process


def generate_name(root: str):
    rootpath = Path(root)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    return rootpath.joinpath(f"scalone {date}.pdf")
