import argparse
from pathlib import Path
import rich_argparse
from implementation.merge import merge_documents
from implementation.configuration import Configuration
from implementation import configuration
from implementation.files import generate_name, recurse_files
from sys import exit


def parse_arguments(default_output_dir: Path, help_override: bool = False):
    rich_argparse.RichHelpFormatter.styles["argparse.metavar"] = "magenta"
    rich_argparse.RichHelpFormatter.styles["argparse.prog"] = "b i"
    rich_argparse.RichHelpFormatter.styles["argparse.groups"] = "dark_orange b"
    parser = argparse.ArgumentParser(
        formatter_class=(lambda prog: rich_argparse.RichHelpFormatter(prog, max_help_position=12)),
        add_help=False,
        prefix_chars="-/",
        # formatter_class=argparse.RawTextHelpFormatter,
        # formatter_class=argparse_formatter.ParagraphFormatter,
        # prog=Path(__file__).name,
        description="Merges given PDFs, images and OpenDocument formats into a single PDF file.",
        epilog="",
    )
    parser.add_argument(
        "-h",
        "-?",
        "--help",
        action="help",
        help="Show this help message and exit.",
    )
    # CORE INPUT
    parser.add_argument(
        "files",
        nargs="*",
        # type=get_files_single,
        help=(
            "Directories and files to be processed.\n"
            "Directories will be searched recursively looking for images, pdfs and OpenDocument formats. "
            "Relative paths are based in the current working directory."
        ),
    )
    parser.add_argument(
        "-s",
        "--save-config",
        metavar="NEW_CONFIG_PATH",
        action="store",
        type=str,
        help="If a path is provided, all input parameters are saved as a config file, under the given path.",
    )
    # PARAMETERS
    parameters_args = parser.add_argument_group("Input parameters")
    parameters_args.description = (
        "All parameters in this group can be stored in a configuration file. "
        "When running the application first the configuration file is read, "
        "then it is updated with commandline parameters."
    )
    parameters_args.add_argument(
        "-c",
        "--config",
        action="store",
        metavar="PATH_TO_CONFIG",
        help=(
            "Custom path to a configuration file. Will be used in place of the default configuration file.\n\n"
            "Some parameters cannot be saved (e.g. files or output_file)."
        ),
    )
    parameters_args.add_argument(
        "-p",
        "--image-page-fallback-size",
        action="store",
        metavar="PAGE_SIZE",
        help=configuration.IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION,
    )
    parameters_args.add_argument("-m", "--margin", action="store", help=configuration.MARGIN_DESCRIPTION)
    parameters_args.add_argument(
        "-fp",
        "--force-image-page-fallback-size",
        action=argparse.BooleanOptionalAction,
        help=configuration.FORCE_IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION,
    )
    parameters_args.add_argument(
        "--alphabetic-file-sorting",
        action=argparse.BooleanOptionalAction,
        help=configuration.ALPHABETIC_FILE_SORTING_DESCRIPTION,
    )
    parameters_args.add_argument(
        "--confirm-exit",
        action=argparse.BooleanOptionalAction,
        help=configuration.CONFIRM_EXIT_DESCRIPTION,
    )
    parameters_args.add_argument(
        "--quiet",
        action=argparse.BooleanOptionalAction,
        help=configuration.QUIET_DESCRIPTION,
    )
    # OUTPUT ARGS
    output_args = parser.add_argument_group(
        "Output",
    )
    output_args.description = (
        "You can specify either output filepath or output directory. "
        "When the directory path is provided the output filename will be generated based on the current date."
    )
    exclusive_output = output_args.add_mutually_exclusive_group()
    exclusive_output.add_argument(
        "-od",
        "--output-directory",
        action="store",
        help="Path of the directory where the output file will be placed. "
        'Filename will be generated based on time and language. Default: "."',
    )
    exclusive_output.add_argument(
        "-o",
        "-of",
        "--output-file",
        action="store",
        help="Path of the output file. " 'Extension will be changed to ".pdf".',
    )
    args, _ = parser.parse_known_args()
    if not args.files or help_override:
        parser.print_help()
        exit()
    return args


def get_default_config_path(__file__):
    return Path(__file__).parent.joinpath("config.toml")


if __name__ == "__main__":
    default_config_path = get_default_config_path(__file__)
    if not default_config_path.exists():
        Configuration().save_config(default_config_path)
        print("Generated default configuration file.")
    default_output = Path(__file__).parent
    args = parse_arguments(default_output)
    config_path = args.config or default_config_path
    config = Configuration()
    if not Path(config_path).exists():
        print(f"Configuration file {config_path} cannot be found. Aborting...")
        exit()
    config.update_from_toml(config_path)
    config.update_from_dictlike(vars(args))
    if args.save_config:
        config.save_config(args.save_config)
        print(f"Configuration saved to {args.save_config}")
    files_to_process = recurse_files(args.files, config.alphabetic_file_sorting)
    output = generate_name(config.output_directory)
    merge_documents(files_to_process, output, config)
    if config.confirm_exit and not config.quiet:
        input("Wcisnij cokolwiek by zamknac")
