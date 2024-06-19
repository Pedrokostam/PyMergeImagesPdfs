from pathlib import Path
from natsort import natsorted, ns
import datetime

from .logger import get_quiet, printline, printlog

# fmt: off
# extensions copy-pasted from Open File windows in LibreOffice
text_documents = [
    ".oth", ".odt", ".ott", ".fodt",
    ".sxw", ".stw",
    ".xml",
    ".docx", ".docm", ".dotx", ".dotm", ".doc",
    ".rtf", ".wps", ".dot", ".wpt", ".hwp",
    ".html", ".xhtml", ".htm",
    ".lwp", ".psw", ".txt", ".wpd", ".odm",
    ]
calc_documents = [
    ".ods", ".ots", ".sxc", ".stc", ".fods",
    ".xml", ".csv",
    ".xlsx", ".xltx", ".xltm", ".xlsb",
    ".xls", ".xlc", ".xlm", ".xlw", ".xlk", ".xlt",
    ".et", ".ett", ".dif", ".wk1", ".wks", ".123", ".wb2",
    ]
presentation_documents = [
    ".odp", ".otp", ".sti", ".sxd", ".fodp", ".xml",
    ".pptx", ".ppsx", ".potx", ".potm", ".ppt",
    ".dps", ".pps", ".pot", ".dpt",
    ]
drawing_documents = [
    ".odg", ".otg", ".sxd", ".std", ".cdr",
    ".pub", ".vdx", ".vsd", ".vsdm", ".vsdx", ".svg"
    ]
all_image_formats = set([
    ".jpeg", ".jpg", ".tiff", ".png"
    ])
all_pdf_formats = set([
    ".pdf"
    ])
# fmt: on

all_document_formats = set(text_documents + calc_documents + presentation_documents + drawing_documents)
all_formats = all_pdf_formats.union(all_image_formats).union(all_document_formats)


def is_pdf_extension(path: Path):
    return path.suffix.casefold() in all_pdf_formats


def is_image_extension(path: Path):
    suffix = path.suffix.casefold()
    return suffix in all_image_formats


def is_document_extension(path: Path):
    suffix = path.suffix.casefold()
    return suffix in all_document_formats


def is_valid_extensions(path: Path):
    suffix = path.suffix.casefold()
    return suffix in all_formats


def print_entry(path: Path, indent: int):
    if get_quiet():
        return
    indentation = "| " * indent
    msg = indentation + "|-" + str(path.absolute())
    print(msg.encode("utf8").decode("utf8"))


def recurse_impl(path: Path, collection: list[Path], depth: int):
    if path.is_file():
        if is_valid_extensions(path):
            collection.append(path)
            print_entry(path, depth)
    if path.is_dir():
        print_entry(path, depth)
        for subentry in natsorted(path.glob("*"), alg=ns.IGNORECASE):
            recurse_impl(subentry, collection, depth + 1)


def recurse_files(paths: list[str], sort_paths: bool):
    files_to_process: list[Path] = []
    if sort_paths:
        paths = sorted(paths, key=lambda x: x.casefold())
        printlog("InputSorted")
        printline()
    for path in paths:
        recurse_impl(Path(path), files_to_process, 0)
    return files_to_process


def generate_name(root: str):
    rootpath = Path(root)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    return rootpath.joinpath(f"scalone {date}.pdf")
