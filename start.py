import argparse
from typing import Sequence, Union
import pymupdf
from pathlib import Path
import rich_argparse
from logic.file_getter import get_files, get_files_single, is_image
from logic.parameters import load_config, save_config
from logic import parameters
from logic.pdf import convert_image, get_parameters
from logic.pdf_wrapper import process
from logic.translator import TRANSLATOR as T

PathLike = str | Path


def is_pdf_extension(path: Path):
    return path.suffix.casefold() == ".pdf"


def is_image_extensions(path: Path):
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
    output_file = pymupdf.Document()
    actual_pagesize = pymupdf.paper_rect(pagesize)
    if pdf_filepaths:
        first_doc = pymupdf.open(pdf_filepaths[0])
        actual_pagesize = first_doc.load_page(0).rect
    for file in all_filepaths:
        if is_pdf_extension(file):
            output_file.insert_file(str(file))
        elif is_image_extensions(file):
            new_page = output_file.new_page(width=actual_pagesize.width, height=actual_pagesize.height)  # type: ignore
            point_margin = cm_to_points(margin)
            margined_rect = rect_subtract(new_page.rect, point_margin)
            new_page.insert_image(margined_rect, filename=str(file))
        else:
            print(f"Unknown file type: {file}")
    output_file.save(output)


def parse_arguments():
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
        type=get_files_single,
        help=(
            "Directories and files to be processed.\n"
            "Directories will be searched recursively looking for images or pdfs."
        ),
    )
    # parser.add_argument(
    #     "--whatif",
    #     action="store_true",
    #     help="If present, does everything except saving the final merging and saving",
    # )
    # parser.add_argument(
    #     "-l",
    #     "--language",
    #     action="store",
    #     default=parameters.PARAMETERS.get("language", "lll"),
    #     help="Language to be used for messages.",
    # )
    # parser.add_argument(
    #     "-c",
    #     "--config",
    #     action="store_true",
    #     help="If True, creates config file and exits.",
    # )
    # size_args = parser.add_argument_group(
    #     "size",
    #     description=(
    #         "Sizes can be specified by axes (e.g. 21cmx10cm) or by paper size (e.g. A4, B4).\n"
    #         "Size units can be mm, cm, in, pt (default).\n"
    #         "Border and image sizes can be be specified as percentages of page size (50% or 50%x75%) (page size has to be specified!).\n"
    #         "Can also specify empty string or null or none"
    #     ),
    # )
    # size_args.add_argument(
    #     "-p",
    #     "--pagesize",
    #     action="store",
    #     help="Specifies the page size. Dimensions are separated by 'x'.",
    #     default=parameters.PARAMETERS.get("pagesize", None),
    # )
    # size_args_borderimage = size_args.add_mutually_exclusive_group()
    # size_args_borderimage.add_argument(
    #     "-i",
    #     "--imagesize",
    #     action="store",
    #     help="Specifies the maximum image size. Dimensions are separated by 'x'.",
    #     default=parameters.PARAMETERS.get("imagesize", None),
    # )
    # size_args_borderimage.add_argument(
    #     "-b",
    #     "--bordersize",
    #     action="store",
    #     help="Specifies the minimum border size. Dimensions are separated by ':'.",
    #     default=parameters.PARAMETERS.get("bordersize", None),
    # )

    # transformation_args = parser.add_argument_group(
    #     "transformation",
    # ).add_mutually_exclusive_group()
    # transformation_args.add_argument(
    #     "--auto-orient",
    #     action="store_true",
    #     help="If present, will rotate PDF page, to make the image fit better.",
    # )
    # transformation_args.add_argument(
    #     "-r",
    #     "--rotation",
    #     action="store",
    #     help="Rotation of images",
    #     choices=["0", "90", "180", "270", "auto", "ifvalid"],
    #     default=parameters.PARAMETERS.get("rotation", None),
    # )

    output_args = parser.add_argument_group(
        "output",
    ).add_mutually_exclusive_group()
    output_args.add_argument(
        "-o",
        "-od",
        "--output-directory",
        action="store",
        help="Path of the directory where ther output file will be placed. Filename will be generated based on time and language.",
        default=parameters.PARAMETERS.get("output_directory", None),
    )
    output_args.add_argument(
        "-of",
        "--output-file",
        help="Destination path of the output file.",
        default=parameters.PARAMETERS.get("output_file", None),
    )
    output_args.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="If present, will override destination file if it exists.",
        default=parameters.PARAMETERS.get("force", None),
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()
    for path in args.files:
        pathpath = Path(path)
        if pathpath.is_dir():
            pathpath.glob
    merge(
        (
            r"C:\Users\Pedro\Documents\Github\PyMergeImagesPdfs\test\10x10.pdf",
            r"C:\Users\Pedro\Documents\Github\PyMergeImagesPdfs\test\eva.png",
        ),
        "pol.pdf",
        "A4",
        margin=(1, 1),
    )
