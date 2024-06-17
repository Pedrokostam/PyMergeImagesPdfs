from pathlib import Path
from natsort import natsorted, ns
import datetime

# extensions copy-pasted from Open File windows in LibreOffice
text_documents = [
    ".oth",
    ".odt",
    ".ott",
    ".sxw",
    ".stw",
    ".fodt",
    ".xml",
    ".docx",
    ".docm",
    ".dotx",
    ".dotm",
    ".doc",
    ".rtf",
    ".doc",
    ".wps",
    ".dot",
    ".wpt",
    ".hwp",
    ".html",
    ".xhtml",
    ".htm",
    ".lwp",
    ".psw",
    ".txt",
    ".wpd",
    ".odm",
]
calc_documents = [
    ".ods",
    ".ots",
    ".sxc",
    ".stc",
    ".fods",
    ".xml",
    ".xlsx",
    ".xltx",
    ".xltm",
    ".xlsb",
    ".xls",
    ".xlc",
    ".xlm",
    ".xlw",
    ".xlk",
    ".et",
    ".xlt",
    ".ett",
    ".dif",
    ".wk1",
    ".wks",
    ".123",
    ".wb2",
    ".csv",
]
presentation_documents = [
    ".odp",
    ".otp",
    ".sti",
    ".sxd",
    ".fodp",
    ".xml",
    ".pptx",
    ".ppsx",
    ".potx",
    ".potm",
    ".ppt",
    ".dps",
    ".pps",
    ".pot",
    ".dpt",
]
drawing_documents = [".odg", ".otg", ".sxd", ".std", ".cdr", ".pub", ".vdx", ".vsd", ".vsdm", ".vsdx", ".svg"]
all_document_formats = set(text_documents + calc_documents + presentation_documents + drawing_documents)
all_image_formats = set([".jpeg", ".jpg", ".tiff", ".png"])
all_pdf_formats = set([".pdf"])
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


def recurse_files(paths: list[str]):
    files_to_process: list[Path] = []
    for path in paths:
        pathpath = Path(path)
        if pathpath.is_dir():
            subfiles: list[Path] = []
            for f in pathpath.glob("**/*"):
                if is_valid_extensions(f):
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
