from pathlib import Path
from natsort import natsorted, ns
import datetime

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


def recurse_files(paths: list[str], sort_paths: bool):
    files_to_process: list[Path] = []
    if sort_paths:
        paths = sorted(paths, key=lambda x: x.casefold())
    for path in paths:
        pathpath = Path(path)
        if pathpath.is_dir():
            subfiles: list[Path] = []
            # print("DIR  "+str(pathpath))
            for f in pathpath.glob("**/*"):
                if is_valid_extensions(f):
                    # print("        "+str(f.relative_to(pathpath)))
                    subfiles.append(f)
                else:
                    pass
                    # log("FileSkipped",f)
            subfiles = natsorted(subfiles, alg=ns.IGNORECASE)
            files_to_process.extend(subfiles)
        else:
            # print("FILE "+str(pathpath))
            files_to_process.append(pathpath)
    return files_to_process


def generate_name(root: str):
    rootpath = Path(root)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    return rootpath.joinpath(f"scalone {date}.pdf")
