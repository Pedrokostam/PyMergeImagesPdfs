import sys
from pathlib import Path
import click
from logic.configuration import load_config, set_language, set_output_path, save_config, set_page_size
from logic.file_getter import get_files
from logic.pdf_wrapper import process

PROGRAM_FOLDER = Path(globals().get("__file__", sys.argv[0])).parent


@click.command
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True, path_type=Path),
)
@click.option(
    "-c",
    "config",
    is_flag=True,
    help="If True, creates config file and exits.",
)
@click.option(
    "-l",
    "--language",
    help="Language to be used for messages.",
)
@click.option(
    "-s",
    "--size",
    help="""Size for pages from converted images.\n
    Accepts size in units (e.g. '10cm x 50in', default unit is point) and common formats (e.g. A4).\n
    '^T' transposes dimensions""",
    show_default=True,
    default='A4'
)
@click.option("-o", "--output", help="Folder where the merged file will be placed.")
def merge(paths: tuple[Path], size: str, language: str | None = None, output: str | None = None, config: bool = False):
    """
    Accepts paths to files and folders.

    File have to be either images or PDFs.
    Folders will be traversed looking for all images and PDFs.

    You can mix folders and paths.
    """
    load_config(PROGRAM_FOLDER)
    if language:
        set_language(language)
    if output:
        set_output_path(output)
    if size:
        set_page_size(size)
    if config:
        save_config(PROGRAM_FOLDER)
        return
    if not paths:
        click.echo(click.get_current_context().get_help())
        return
    files = get_files(paths)
    process(files)


if __name__ == "__main__":
    merge()
