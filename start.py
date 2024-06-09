import argparse
from pathlib import Path
import rich_argparse
from implementation.merge import merge
from implementation.config import Config
from implementation.files import generate_name, recurse_files


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
    output_args.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="If present, will override destination file if it exists.",
        default=False,
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    if not Path("./config.toml").exists():
        Config().save_config("./config.toml")
        exit()

    config = Config()
    config.update("./config.toml")
    default_output = Path(__file__).parent
    args = parse_arguments(default_output)
    files_to_process = recurse_files(args.files)
    output = generate_name(args.output_directory)
    merge(files_to_process, output, config)
    input("Wcisnij cokolwiek by zamknac")
