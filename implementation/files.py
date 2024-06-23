import datetime
from itertools import pairwise, takewhile
from pathlib import Path
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


TREE_ROOT = "╚═╗"
TREE_PREFIX = "   "
BRANCH = "│  "
NO_BRANCH = "   "
TEE = "├──"
END = "└──"
ROOT_BRANCH_CONT = "╟"
SUB_BRANCH_CONT = "├"
ROOT_BRANCH_END = "╙"
SUB_BRANCH_END = "└"
NEST_PADDING = 4


def recurse_impl(path: Path, collection: list[Path], current_depth: int, recursion_limit: int):
    if path.is_file():
        if is_valid_extensions(path):
            collection.append(path.absolute())
            # print_entry(path, current_depth)
    # not a file and recursion limit met
    if current_depth >= recursion_limit:
        return
    if path.is_dir():
        # print_entry(path, current_depth)
        collection.append(path.absolute())
        sorted_entries = sorted(natsorted(path.glob("*"), alg=ns.IGNORECASE), key=lambda x: x.is_dir(), reverse=False)
        for subentry in sorted_entries:
            recurse_impl(subentry, collection, current_depth=current_depth + 1, recursion_limit=recursion_limit)


class FoldedPath:

    def __init__(self, path: Path | str, is_last: bool) -> None:
        self.path = Path(path)
        self.subpaths: list[FoldedPath] = []
        self.is_last = is_last

    def populate(self, current_depth: int, max_depth: int):
        if not self.path.is_dir():
            return
        sorted_entries = sorted(
            natsorted(self.path.glob("*"), alg=ns.IGNORECASE), key=lambda x: x.is_dir(), reverse=False
        )
        if current_depth + 1 >= max_depth:
            sorted_entries = [s for s in sorted_entries if not s.is_dir()]
        sorted_count = len(sorted_entries)
        for i, entry in enumerate(sorted_entries):
            if entry.is_dir() and current_depth + 1 >= max_depth:
                continue
            self.subpaths.append(FoldedPath(entry, i + 1 == sorted_count))
            self.subpaths[-1].populate(current_depth + 1, max_depth)

    def display_form(self, is_root: bool):
        if not self.is_dir():
            color = "\033[33m{0}\033[0m"
        else:
            color = "{0}"
        name = str(self.path.absolute()) if is_root else self.path.name
        return color.format(name)

    def is_dir(self):
        return self.path.is_dir()

    def __repr__(self):
        return f"{self.path} - {len(self.subpaths)}"

    def print(self, is_root: bool = True, depth: list[bool] = []):
        if get_quiet():
            return
        line = ""
        for d in depth:
            line += BRANCH if d else NO_BRANCH
        line += END if self.is_last else TEE
        print(line + self.display_form(is_root))
        for s in self.subpaths:
            s.print(False, depth + [not self.is_last])


def recurse_files(paths: list[str], sort_paths: bool, recursion_limit: int):
    filesystem_entries: list[Path] = []
    if sort_paths:
        paths = sorted(paths, key=lambda x: x.casefold())
        printlog("InputSorted")
        printline()
    folded_paths: list[FoldedPath] = []
    for i, path in enumerate(paths):
        folded_paths.append(FoldedPath(path, i + 1 == len(paths)))
        folded_paths[-1].populate(0, recursion_limit)
        folded_paths[-1].print()

        # recurse_impl(Path(path), filesystem_entries, current_depth=0, recursion_limit=recursion_limit)
    exit()
    files = [f for f in filesystem_entries if f.is_file()]
    return files


def generate_name(root: str | Path):
    rootpath = Path(root)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    return rootpath.joinpath(f"scalone {date}.pdf")
