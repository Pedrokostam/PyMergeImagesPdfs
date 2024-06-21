import argparse
from pathlib import Path
import sys
import rich_argparse
from implementation.merge import merge_documents
from implementation.configuration import Configuration
from implementation import configuration
from implementation.files import generate_name, recurse_files
from sys import exit
from implementation.logger import printline, printlog, log, set_language_from_file, set_quiet

PROGRAM_DIR = Path(__file__).parent


def parse_arguments(help_override: bool = False):
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
        help="Path of the output file. Relative to the current working directory."
        'Extension will be changed to ".pdf".',
    )
    args, _ = parser.parse_known_args()
    if not args.files or help_override:
        parser.print_help()
        exit()
    set_quiet(args.quiet)
    return args


def regenerate_default_config(default_config_path: Path):
    if not default_config_path.exists():
        Configuration().save_config(default_config_path)
        # printlog("GeneratedDefaultConfig")


def load_config(cmd_args, default_config_path):
    config_path = cmd_args.config or default_config_path
    config = Configuration()
    if not Path(config_path).exists():
        printlog("ConfigNotFound", config_path)
        exit()
    config.update_from_toml(config_path)
    config.update_from_dictlike(vars(cmd_args))
    set_quiet(config.quiet)
    return config


def wait_for_confirm(wait: bool):
    if wait:
        try:
            input("\n" + str(log("ConfirmExit")))
        except KeyboardInterrupt:  # CTRL-C should gracefully exit now
            pass


if __name__ == "__main__":
    # REGENERATE CONFIG
    default_config_path = PROGRAM_DIR.joinpath("config.toml")
    regenerate_default_config(default_config_path)
    # LOAD LANGUAGE
    set_language_from_file(PROGRAM_DIR.joinpath("language.json"))
    # PARSE ARGS
    args = parse_arguments()
    # LOAD CONFIG
    config = load_config(args, default_config_path)
    # MAYBE SAVE CONFIG
    if args.save_config:
        config.save_config(args.save_config)
    # GET FILES
    files_to_process = recurse_files(args.files, config.alphabetic_file_sorting)
    # GET OUTPUT PATH
    if args.output_file:  # Output_file has precedence if specified
        output = Path(args.output_file)
    else:
        output = generate_name(config.output_directory_expanded(PROGRAM_DIR))
    # MERGE
    merge_documents(files_to_process, output, config)
    # WAIT FOR CONFIRM
    wait_for_confirm(wait=config.confirm_exit and not config.quiet)
