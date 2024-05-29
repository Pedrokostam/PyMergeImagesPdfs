import argparse
import datetime
from typing import Sequence
import pymupdf
from pathlib import Path
import rich_argparse
from natsort import natsorted, ns

from implementation.config import Config

PathLike = str | Path


def is_pdf_extension(path: Path):
    return path.suffix.casefold() == ".pdf"


def is_image_extension(path: Path):
    suffix = path.suffix.casefold()
    return suffix in [".jpeg", ".jpg", ".tiff", ".png"]


def cm_to_points(cm_tuple: tuple[float, float]):
    return (cm_tuple[0] / 2.54 * 72, cm_tuple[1] / 2.54 * 72)


def rect_subtract(minuend: pymupdf.Rect, subtrahend_points: tuple[float, float]):
    return pymupdf.Rect(
        subtrahend_points[0],
        subtrahend_points[0],
        minuend.width - subtrahend_points[0],
        minuend.height - subtrahend_points[1],
    )


def merge(files: Sequence[PathLike], output: PathLike, pagesize: str, *, margin: tuple[float, float] = (0, 0)):
    all_filepaths = [Path(x) for x in files]
    pdf_filepaths = [x for x in all_filepaths if is_pdf_extension(x)]
    output = Path(output).absolute()
    output_file = pymupdf.Document()
    actual_pagesize = pymupdf.paper_rect(pagesize)
    if pdf_filepaths:
        first_doc = pymupdf.open(pdf_filepaths[0])
        actual_pagesize = first_doc.load_page(0).rect
    for file in all_filepaths:
        print(f"Zszywanie: {file}")
        if is_pdf_extension(file):
            output_file.insert_file(str(file))
        elif is_image_extension(file):
            img = pymupdf.open(file)
            img_pdf_bytes = img.convert_to_pdf()
            img.close()
            img_pdf = pymupdf.open("pdf", img_pdf_bytes)
            new_page = output_file.new_page(width=actual_pagesize.width, height=actual_pagesize.height)  # type: ignore
            point_margin = cm_to_points(margin)
            margined_rect = rect_subtract(new_page.rect, point_margin)
            new_page.show_pdf_page(margined_rect, img_pdf, pno=0, keep_proportion=True, rotate=0)
        else:
            print(f"Unknown file type: {file}")
    output_file.save(str(output))
    print(f"Zapisano w {output}")


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


def parse_arguments(default_output_dir: Path):
    rich_argparse.RichHelpFormatter.styles["argparse.metavar"] = "magenta"
    rich_argparse.RichHelpFormatter.styles["argparse.prog"] = "b i"
    rich_argparse.RichHelpFormatter.styles["argparse.groups"] = "dark_orange b"
    parser = argparse.ArgumentParser(
        formatter_class=rich_argparse.RawTextRichHelpFormatter,
        # formatter_class=argparse.RawTextHelpFormatter,
        # formatter_class=argparse_formatter.ParagraphFormatter,
        prog="merge",
        description="Merges given PDFs and images into a single PDF file",
        epilog="",
    )
    parser.add_argument(
        "files",
        nargs="*",
        # type=get_files_single,
        help=(
            "Directories and files to be processed.\n"
            "Directories will be searched recursively looking for images or pdfs."
        ),
    )
    output_args = parser.add_argument_group(
        "output",
    )

    exclusive_output = output_args.add_mutually_exclusive_group()
    exclusive_output.add_argument(
        "-o",
        "-od",
        "--output-directory",
        action="store",
        help="Path of the directory where ther output file will be placed. Filename will be generated based on time and language.",
        default=default_output_dir,
    )
    # exclusive_output.add_argument(
    #     "-of",
    #     "--output-file",
    #     help="Destination path of the output file.",
    #     default=None,
    # )
    # output_args.add_argument(
    #     "-f",
    #     "--force",
    #     action="store_true",
    #     help="If present, will override destination file if it exists.",
    #     default=False,
    # )
    args = parser.parse_args()
    return args


def get_default_output_path():
    Config().save_config('./config.toml')
    script_path = Path(__file__)
    config_path: Path
    if script_path.parent.name == "_internal":
        config_path = script_path.parent.parent.joinpath("config.txt")
    else:
        config_path = script_path.parent.joinpath("config.txt")
    if config_path.exists():
        with open(config_path, "r") as cf:
            return Path(cf.readline().strip())
    return Path(".")


if __name__ == "__main__":
    default_output = get_default_output_path()
    args = parse_arguments(default_output)
    files_to_process = recurse_files(args.files)
    output = generate_name(args.output_directory)
    merge(
        files_to_process,
        output,
        "A4",
        margin=(0, 0),
    )
    input("Wcisnij cokolwiek by zamknac")
