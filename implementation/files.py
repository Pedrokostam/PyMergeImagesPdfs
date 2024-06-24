import datetime
from operator import methodcaller
from pathlib import Path
from typing import Any, Generator
from natsort import natsorted, ns
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
    ".jpeg", ".jpg", ".tiff", ".png", ".bmp", ".pnm", ".pbm", ".pam", ".jxr", ".jpx", ".jp2", ".psd"
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


TREE_PREFIX = "   "
BRANCH = "│  "
ROOT_BRANCH = "║  "
NO_BRANCH = "   "
TEE = "├──"
ROOT_TEE = "╠══"
END = "└──"
ROOT_END = "╚══"
DIR_JUNCTION = "┬"
ROOT_DIR_JUNCTION = "╤"


def get_junction(root: bool = False):
    return ROOT_DIR_JUNCTION if root else DIR_JUNCTION


def get_tee(root: bool = False):
    return ROOT_TEE if root else TEE


def get_end(root: bool = False):
    return ROOT_END if root else END


def get_branch(root: bool = False):
    return ROOT_BRANCH if root else BRANCH


def is_supported_entry(path: Path):
    return path.is_dir() or path.suffix.lower() in all_formats


class FoldedPath:

    def __init__(self, path: Path | str, is_last: bool) -> None:
        self.path = Path(path)
        self.subpaths: list[FoldedPath] = []
        self.is_last = is_last

    def populate(self, current_depth: int, max_depth: int):
        if not self.path.is_dir():
            return

        filtered_entries = [e for e in self.path.glob("*") if is_supported_entry(e)]
        dir_checker = methodcaller("is_dir")
        sorted_entries = sorted(natsorted(filtered_entries, alg=ns.IGNORECASE), key=dir_checker, reverse=False)
        if current_depth + 1 >= max_depth:
            sorted_entries = [s for s in sorted_entries if not s.is_dir()]
        sorted_count = len(sorted_entries)
        for i, entry in enumerate(sorted_entries):
            if entry.is_dir() and current_depth + 1 >= max_depth:
                continue
            self.subpaths.append(FoldedPath(entry, i + 1 == sorted_count))
            self.subpaths[-1].populate(current_depth + 1, max_depth)

    def display_form(self, is_root: bool):
        # junction = get_junction(is_root) if self.is_dir() else ""
        junction = ""
        if not self.is_dir():
            color = "\033[32m{0}\033[0m"
        else:
            color = "{0}"
        name = str(self.path.absolute()) if is_root else self.path.name
        return junction + color.format(name)

    def is_dir(self):
        return self.path.is_dir()

    def __repr__(self):
        return f"{self.path} - {len(self.subpaths)}"

    def print(self, is_root: bool = True, depth: list[bool] | None = None):
        if get_quiet():
            return
        line = ""
        for i, d in enumerate(depth or []):
            line += get_branch(i == 0) if d else NO_BRANCH
        line += get_end(is_root) if self.is_last else get_tee(is_root)
        print(line + self.display_form(is_root))
        for s in self.subpaths:
            s.print(False, (depth or []) + [not self.is_last])

    def get_files(self) -> Generator["FoldedPath", Any, None]:
        for s in self.subpaths:
            if s.is_dir():
                yield from s.get_files()
            else:
                yield s


def recurse_files(paths: list[str], sort_paths: bool, recursion_limit: int):
    if sort_paths:
        paths = sorted(paths, key=lambda x: x.casefold())
        printlog("InputSorted")
        printline()
    folded_paths: list[FoldedPath] = []
    printlog("FilesToProcess")
    for i, path in enumerate(paths):
        folded_paths.append(FoldedPath(path, i + 1 == len(paths)))
        folded_paths[-1].populate(0, recursion_limit)
        folded_paths[-1].print()
    files = [s.path for f in folded_paths for s in f.get_files()]
    return files


def generate_name(root: str | Path):
    rootpath = Path(root)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    return rootpath.joinpath(f"scalone {date}.pdf")
