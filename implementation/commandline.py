import argparse
import inspect
import sys
from pathlib import Path
from typing import Any

import rich_argparse
import rich.terminal_theme
from colorama import just_fix_windows_console

from implementation import configuration
from implementation.configuration import Configuration
from implementation.logger import print_translated, set_quiet, translate

from .custom_rich_argparse_formatters import RawTextIndentArgumentsDefaultRichHelpFormatter


class Dummy:
    """Wrapper class, which is displayed as the inner object,
    but allows to check if the parameter has been set from the command line,
    or is the default value."""

    def __init__(self, obj) -> None:
        self._obj = obj

    def __repr__(self):
        if self._obj == "":
            return '""'
        return repr(self._obj)

    def __str__(self):
        if self._obj == "":
            return '""'
        return str(self._obj)

    @staticmethod
    def nullify_dummies(args: argparse.Namespace):
        """Checks all arguments to see if they are a Dummy and replaces it with None if it is."""
        for k, v in vars(args).items():
            if isinstance(v, Dummy):
                setattr(args, k, None)


DESCRIPTION = """
Merges given PDFs, images and office document formats into a single PDF file.

The program accepts both file and folders (which are recursively scanned for supported files.)

Most of the parameters can be loaded from a configuration file.\
    
A configuration file with default values is automatically created if it does not exists.\
    
Its path is config.toml. It will always be loaded when the program runs (unless a different file is specified via --config)

Flag options have their negative variant to override parameters loaded from the configuration file.\

(With the default configuration file they are not needed)

Default values shown in help are not loaded from any configuration file.
"""

EPILOG = """
To use the program by drag&dropping files and folders onto it, enable the config_dragdrop.toml which should be provided.

To enable change it name to config.toml, or add --config config_dragdrop.toml as an arguments to the shortcut or script you want to drop file onto.
"""


def wait_for_confirm(wait: bool):
    if wait:
        try:
            input("\n" + str(translate("ConfirmExit")))
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
        print_translated("ConfigNotFound", config_path)
        sys.exit()
    config.update_from_toml(config_path)
    config.update_from_dictlike(vars(cmd_args))
    set_quiet(config.quiet)
    return config


def parse_arguments(help_override: bool = False):
    just_fix_windows_console()
    # "argparse.args": "cyan", for positional-arguments and --options (e.g "--help")
    # "argparse.groups": "dark_orange", for group names (e.g. "positional arguments")
    # "argparse.help": "default", for argument's help text (e.g. "show this help message and exit")
    # "argparse.metavar": "dark_cyan", for meta variables (e.g. "FILE" in "--file FILE")
    # "argparse.syntax": "bold", for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
    # "argparse.text": "default", for highlights of back-tick quoted text (e.g. "``` `some text` ```")
    # "argparse.prog": "grey50", for the descriptions and epilog (e.g. "A foo program")
    # "argparse.default": "italic",  for %(default)s in the help (e.g. "Value" in "(default: Value)")
    rich_argparse.RichHelpFormatter.styles["argparse.metavar"] = "spring_green1 italic"
    rich_argparse.RichHelpFormatter.styles["argparse.args"] = "deep_sky_blue1 bold"
    rich_argparse.RichHelpFormatter.styles["argparse.prog"] = "bold italic orange_red1"
    rich_argparse.RichHelpFormatter.styles["argparse.text"] = "default"
    rich_argparse.RichHelpFormatter.styles["argparse.groups"] = "orange3 bold"
    rich_argparse.RichHelpFormatter.styles["argparse.syntax"] = "red"
    rich_argparse.RichHelpFormatter.styles["argparse.default"] = "italic dim"
    rich_argparse.RichHelpFormatter.styles["argparse.help"] = "default"
    rich_argparse.RichHelpFormatter.styles["argparse.toml"] = "bold slate_blue1"
    rich_argparse.RichHelpFormatter.highlights.append(r"(?i)\b(?P<toml>(\w+\.)?toml)\b")
    dummy_config = Configuration()
    epilog: Any = inspect.cleandoc(EPILOG)
    description: Any = inspect.cleandoc(DESCRIPTION)
    parser = argparse.ArgumentParser(
        formatter_class=(lambda prog: RawTextIndentArgumentsDefaultRichHelpFormatter(prog, max_help_position=8)),
        add_help=False,
        prefix_chars="-/",
        # formatter_class=argparse.RawTextHelpFormatter,
        # formatter_class=argparse_formatter.ParagraphFormatter,
        # prog=Path(__file__).name,
        description=description,
        epilog=epilog,
    )
    parser.add_argument(
        "--generate-help-preview",
        action=rich_argparse.HelpPreviewAction,
        path="help-preview.html",  # (optional) or "help-preview.html" or "help-preview.txt"
        export_kwds={"theme": rich.terminal_theme.MONOKAI},  # (optional) keywords passed to console.save_... methods
    )
    parser.add_argument(
        "-h",
        "-?",
        "--help",
        "/?",
        action="help",
        help="Show this help message and exit. Running the app without any files does the same.",
    )
    # CORE INPUT
    parser.add_argument(
        "files",
        nargs="*",
        # type=get_files_single,
        help=(
            "Directories and files to be processed.\n"
            "Directories will be searched recursively looking for images, pdfs and office document formats.\n"
            "Relative paths are based in the current working directory."
        ),
    )
    parser.add_argument(
        "-s",
        "--save-config",
        metavar="FILEPATH or -",
        action="store",
        type=str,
        help="If a path is provided, all input parameters are saved as a TOML configuration file, under the given path.\n"
        "Input parameters are a union of commandline parameters as well as the loaded configuration file's parameters.\n"
        "To send the TOML text to standard output, specify '-' as the destination.\n"
        "After saving the condfiguration the program exits.",
    )
    parser.add_argument(
        "--confirm-exit",
        default=Dummy(dummy_config.confirm_exit),
        action=argparse.BooleanOptionalAction,
        help=configuration.CONFIRM_EXIT_DESCRIPTION,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        default=Dummy(dummy_config.quiet),
        action=argparse.BooleanOptionalAction,
        help=configuration.QUIET_DESCRIPTION,
    )
    parser.add_argument(
        "-whatif",
        "--what-if",
        "--whatif",
        action="store_true",
        default=Dummy(dummy_config.what_if),
        help="If present, runs the program, but outputs no files. Overrides --quiet.",
    )
    parser.add_argument(
        "-l",
        "--language",
        action="store",
        metavar="IDENTIFIER",
        help=configuration.LANGUAGE_DESCRIPTION,
        default=Dummy(dummy_config.language),
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
            "Custom path to a configuration file. Will be used in place of the default configuration file.\n"
            "Some parameters cannot be saved (e.g. files or output_file)."
        ),
    )
    parameters_args.add_argument(
        "--recursion-limit",
        action="store",
        type=int,
        help=configuration.RECURSION_DESCRIPTION,
        default=Dummy(dummy_config.recursion_limit),
    )
    parameters_args.add_argument(
        "-p",
        "--image-page-fallback-size",
        action="store",
        metavar="PAGE_SIZE",
        # pylint: disable=protected-access
        default=Dummy(dummy_config._image_page_fallback_size),
        help=configuration.IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION,
    )
    parameters_args.add_argument(
        "-m",
        "--margin",
        action="store",
        help=configuration.MARGIN_DESCRIPTION,
        # pylint: disable=protected-access
        default=Dummy(dummy_config._margin),
    )
    parameters_args.add_argument(
        "--fp",
        "--force-image-page-fallback-size",
        action=argparse.BooleanOptionalAction,
        default=Dummy(dummy_config.force_image_page_fallback_size),
        help=configuration.FORCE_IMAGE_PAGE_FALLBACK_SIZE_DESCRIPTION,
    )
    parameters_args.add_argument(
        "--afs",
        "--alphabetic-file-sorting",
        default=Dummy(dummy_config.alphabetic_file_sorting),
        action=argparse.BooleanOptionalAction,
        help=configuration.ALPHABETIC_FILE_SORTING_DESCRIPTION,
    )
    parameters_args.add_argument(
        "--libreoffice-path",
        nargs="*",
        # pylint: disable=protected-access
        default=Dummy(dummy_config._libreoffice_path),
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
        default=Dummy(dummy_config.output_directory),
        help="Path of the directory where the output file will be placed. "
        "Filename will be generated based on time and language.\n"
        "This path will always be treated as a folder path, even if you provide an extension.",
    )
    exclusive_output.add_argument(
        "-o",
        "-of",
        "--output-file",
        metavar="OUTPUT_FILEPATH",
        action="store",
        help="Path of the output file. Relative to the current working directory.\n"
        "This path will always be treated as a file path, even if you do not provide an extension.\n"
        'Extension will be changed to ".pdf/.png" as needed.',
    )
    args = parser.parse_args()
    Dummy.nullify_dummies(args)
    if args.what_if:
        args.quiet = False
    if help_override or (not args.files and not args.save_config):
        parser.print_help()
        sys.exit()
    set_quiet(args.quiet)
    return args
