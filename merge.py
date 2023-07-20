import argparse
import datetime
import io
import os
import sys
from pathlib import Path
import PyPDF2
import click
import rich_argparse
import tqdm
from logic.file_getter import get_files, get_files_single, is_image
from logic.parameters import load_config, save_config
from logic import parameters
from logic.pdf import convert_image, get_parameters
from logic.pdf_wrapper import process
from logic.translator import TRANSLATOR as T

PROGRAM_FOLDER = Path(globals().get("__file__", sys.argv[0])).parent


# @click.command
# @click.argument(
#     "paths",
#     nargs=-1,
#     help=T.get("tln_arg_paths"),
#     type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True, path_type=Path),
# )
# @click.option(
#     "-c",
#     "config",
#     is_flag=True,
#     help=T.get("tln_arg_config"),
# )
# @click.option(
#     "-l",
#     "--language",
#     help=T.get("tln_arg_language"),
# )
# @click.option(
#     "-s",
#     "--size",
#     help=T.get("tln_arggrp_size"),
#     show_default=True,
#     default="A4",
# )
# @click.option(
#     "--scale",
#     help=T.get("tln_arg_scale"),
#     show_default=True,
#     type=click.FLOAT,
#     default=1.0,
# )
# @click.option(
#     "--rotation",
#     help="""Rotation to apply to images, in degrees""",
#     show_default=True,
#     type=click.FLOAT,
#     default=0.0,
# )
# @click.option(
#     "--whatif",
#     is_flag=True,
#     help=T.get("tln_arg_whatif"),
# )
# @click.option(
#     "-j",
#     "--jpeg",
#     is_flag=True,
#     help="""If present, all images will be compressed to JPEG if they are not already""",
# )
# @click.option("-o", "--output", help="Folder where the merged file will be placed.")
def merge(
    paths: tuple[Path],
    size: str,
    language: str | None,
    output: str | None,
    config: bool,
    whatif: bool,
    rotation: float,
    scale: float,
    jpeg: bool,
):
    """
    Accepts paths to files and folders.

    File have to be either images or PDFs.
    Folders will be traversed looking for all images and PDFs.

    You can mix folders and paths.
    """
    if not paths:
        click.echo(click.get_current_context().get_help())
        return
    files = get_files(paths)
    process(
        files,
        whatif,
        rotation=rotation,
        scale=scale,
        jpeg=jpeg,
    )


if __name__ == "__main__":
    rich_argparse.RichHelpFormatter.styles["argparse.metavar"] = "magenta"
    rich_argparse.RichHelpFormatter.styles["argparse.prog"] = "b i"
    rich_argparse.RichHelpFormatter.styles["argparse.groups"] = "dark_orange b"
    load_config()
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
            "Files will be treated as images.\n"
            "Directories will be searched recursively looking for images."
        ),
    )
    parser.add_argument(
        "--whatif",
        action="store_true",
        help="If present, does everything except saving the final merging and saving",
    )
    parser.add_argument(
        "-l",
        "--language",
        action="store",
        default=parameters.PARAMETERS.get("language", "lll"),
        help="Language to be used for messages.",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store_true",
        help="If True, creates config file and exits.",
    )
    size_args = parser.add_argument_group(
        "size",
        description=(
            "Sizes can be specified by axes (e.g. 21cmx10cm) or by paper size (e.g. A4, B4).\n"
            "Size units can be mm, cm, in, pt (default).\n"
            "Border and image sizes can be be specified as percentages of page size (50% or 50%x75%) (page size has to be specified!)."
        ),
    )
    size_args.add_argument(
        "-p",
        "--pagesize",
        action="store",
        help="Specifies the page size. Dimensions are separated by 'x'.",
        default=parameters.PARAMETERS.get("pagesize", None),
    )
    size_args_borderimage = size_args.add_mutually_exclusive_group()
    size_args_borderimage.add_argument(
        "-i",
        "--imagesize",
        action="store",
        help="Specifies the maximum image size. Dimensions are separated by 'x'.",
        default=parameters.PARAMETERS.get("imagesize", None),
    )
    size_args_borderimage.add_argument(
        "-b",
        "--bordersize",
        action="store",
        help="Specifies the minimum border size. Dimensions are separated by ':'.",
        default=parameters.PARAMETERS.get("bordersize", None),
    )

    transformation_args = parser.add_argument_group(
        "transformation",
    )
    transformation_args.add_argument(
        "--auto-orient",
        action="store_true",
        help="If present, will rotate PDF page, to make the image fit better.",
    )
    transformation_args.add_argument(
        "-r",
        "--rotation",
        action="store",
        help="Rotation of images",
        choices=['0', '90', '180', '270', "auto", "ifvalid"],
        default=parameters.PARAMETERS.get("rotation", None),
    )

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
    T.set_locale(args.language)
    if args.config:
        save_config(args)
        exit()
    input_files: list[Path] = [Path(file) for array in args.files for file in array]
    pars = vars(args)
    for key, val in parameters.PARAMETERS.items():
        if key not in pars:
            pars[key] = val

    par_dict = get_parameters(input_files, **pars)
    print(par_dict)
    data_array: list[tuple[Path, bytes]] = []
    for file in input_files:
        if is_image(file):
            data = convert_image(file, **par_dict)
        else:
            data = file.read_bytes()
        if data:
            data_array.append((file, data))
    output_file = Path(args.output_file) if args.output_file else None
    output_dir = Path(args.output_directory) if args.output_directory else None
    if output_file:
        destination = output_file
    else:
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
        destination = (output_dir or Path(".")).joinpath(T.get("tln_merged_prefix", date=date_now))
    destination = os.path.expanduser(destination)
    destination = os.path.expandvars(destination)
    with PyPDF2.PdfMerger() as merger:
        merge_bar = tqdm.tqdm(data_array, leave=False)
        info_list: list[str] = []
        for file_to_merge in merge_bar:
            display_name = file_to_merge[0].stem[6:]
            was_image = file_to_merge[0].name[4] == "i"
            merge_bar.set_description_str(display_name)
            merger.append(io.BytesIO(file_to_merge[1]))  # type:ignore
            info_list.append(display_name)
        merger.write(destination)  # type:ignore
