import argparse
from pathlib import Path
import sys
import rich_argparse
from implementation.configuration import Configuration
from implementation import configuration
from .custom_rich_argparse_formatters import RawDescriptionPreservedHelpNewLineDefaultRichHelpFormatter
from implementation.logger import printlog, log, set_quiet
from colorama import just_fix_windows_console

def wait_for_confirm(wait: bool):
    if wait:
        try:
            input("\n" + str(log("ConfirmExit")))
        except KeyboardInterrupt:  # CTRL-C should gracefully exit now
            pass


def regenerate_default_config(default_config_path: Path):
    if not default_config_path.exists():
        Configuration().save_config(default_config_path)
        # printlog("GeneratedDefaultConfig")


def load_config(cmd_args, default_config_path):
    config_path = cmd_args.config or default_config_path
    config = Configuration()
    if not Path(config_path).exists():
        printlog("ConfigNotFound", config_path)
        sys.exit()
    config.update_from_toml(config_path)
    config.update_from_dictlike(vars(cmd_args))
    set_quiet(config.quiet)
    return config


def parse_arguments(help_override: bool = False):
    just_fix_windows_console()
    rich_argparse.RichHelpFormatter.styles["argparse.metavar"] = "magenta"
    rich_argparse.RichHelpFormatter.styles["argparse.prog"] = "bold italic"
    rich_argparse.RichHelpFormatter.styles["argparse.groups"] = "dark_orange bold"
    parser = argparse.ArgumentParser(
        formatter_class=(lambda prog: RawDescriptionPreservedHelpNewLineDefaultRichHelpFormatter(prog, max_help_position=8)),
        add_help=False,
        prefix_chars="-/",
        # formatter_class=argparse.RawTextHelpFormatter,
        # formatter_class=argparse_formatter.ParagraphFormatter,
        # prog=Path(__file__).name,
        description="Merges given PDFs, images and office document formats into a single PDF file.",
    )
    parser.add_argument(
        "-h",
        "-?",
        "--help",
        "/?",
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
            "Directories will be searched recursively looking for images, pdfs and office document formats. "
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
    parser.add_argument(
        "-whatif",
        "--whatif",
        action="store_true",
        help="If present, runs the program, but outputs no files. Overrides --quiet",
    )
    parser.add_argument(
        "-l",
        "--language",
        action="store",
        help=configuration.LANGUAGE_DESCRIPTION
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
        "--recursion-limit",
        action="store",
        type=int,
        help=configuration.RECURSION_DESCRIPTION,
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
        "--fp",
        "--force-image-page-fallback-size",
        action=argparse.BooleanOptionalAction,
        help=configuration.FORCE_IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION,
    )
    parameters_args.add_argument(
        "--afs",
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
        "-q",
        "--quiet",
        action=argparse.BooleanOptionalAction,
        help=configuration.QUIET_DESCRIPTION,
    )
    parameters_args.add_argument(
        "--libreoffice-path",
        nargs="*",
        help=configuration.LIBREOFFICE_PATH_DESCRIPTION,
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
        help="Path of the output file. Relative to the current working directory. "
        'Extension will be changed to ".pdf/.png" as needed.',
    )
    args = parser.parse_args()
    if args.whatif:
        args.quiet = False
    if not args.files or help_override:
        parser.print_help()
        sys.exit()
    set_quiet(args.quiet)
    return args
