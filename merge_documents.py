import argparse
from pathlib import Path
import rich_argparse
from implementation.merge import merge_documents
from implementation.config import Config
from implementation.files import generate_name, recurse_files
from sys import exit


def parse_arguments(default_output_dir: Path, help_override: bool):
    rich_argparse.RichHelpFormatter.styles["argparse.metavar"] = "magenta"
    rich_argparse.RichHelpFormatter.styles["argparse.prog"] = "b i"
    rich_argparse.RichHelpFormatter.styles["argparse.groups"] = "dark_orange b"
    parser = argparse.ArgumentParser(
        formatter_class=rich_argparse.ArgumentDefaultsRichHelpFormatter,
        # formatter_class=argparse.RawTextHelpFormatter,
        # formatter_class=argparse_formatter.ParagraphFormatter,
        # prog=Path(__file__).name,
        description="Merges given PDFs, images and OpenDocument formats into a single PDF file.",
        epilog="",
    )
    # CORE INPUT
    parser.add_argument(
        "files",
        nargs="*",
        # type=get_files_single,
        help=(
            "Directories and files to be processed. "
            "Directories will be searched recursively looking for images, pdfs and OpenDocument formats. "
            "Relative paths are based in the current working directory."
        ),
    )
    # OUTPUT ARGS
    output_args = parser.add_argument_group(
        "output",
    )
    exclusive_output = output_args.add_mutually_exclusive_group()
    exclusive_output.add_argument(
        "-o",
        "-od",
        "--output-directory",
        action="store",
        help="Path of the directory where ther output file will be placed. "
        "Filename will be generated based on time and language.",
        default=default_output_dir,
    )
    output_args.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="If present, will overwrite destination file if it exists.",
        default=False,
    )
    args = parser.parse_args()
    if not args.files or help_override:
        parser.print_help()
        exit()
    return args


if __name__ == "__main__":
    help_override = False
    if not Path("./config.toml").exists():
        Config().save_config(Path(__file__).parent.joinpath("config.toml"))
        help_override = True
    config = Config()
    config.update("./config.toml")
    default_output = Path(__file__).parent
    args = parse_arguments(default_output, help_override)
    files_to_process = recurse_files(args.files)
    output = generate_name(args.output_directory)
    merge_documents(files_to_process, output, config)
    input("Wcisnij cokolwiek by zamknac")
