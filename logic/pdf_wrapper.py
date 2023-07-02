import datetime
from pathlib import Path
import shutil
import tempfile
from typing import Iterable
import click
import img2pdf  # type:ignore
import PyPDF2
from natsort import os_sorted
import tqdm

from .configuration import get_page_size, get_text as TEXT, get_output_path


def convert_image_to_pdf(image_file_path: Path, destination_temp_path: Path, bar: tqdm.tqdm) -> None:
    size = get_page_size().lower().replace(" ", "").replace("^t", "^T")
    error = False
    with open(destination_temp_path, "wb") as pdf_path:
        size_in_pt = img2pdf.parse_pagesize_rectarg(size)  # type:ignore
        layout_fun = img2pdf.get_layout_fun(size_in_pt)  # type:ignore
        try:
            image = img2pdf.convert(str(image_file_path), layout_fun=layout_fun)  # type:ignore
            pdf_path.write(image)  # type:ignore
        except ValueError as e:
            pdf_path.close()
            bar.write(f"{TEXT().msg_conversion_error}{image_file_path.name} ({e})")
            destination_temp_path.unlink(missing_ok=True)
            error = True


def merge_pdf_files(files_to_merge: Iterable[Path]):
    files_to_merge = os_sorted(files_to_merge)
    date_now = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    output = get_output_path().joinpath(f"{TEXT().msg_merged_prefix} {date_now}.pdf")
    with PyPDF2.PdfMerger() as merger:
        merge_bar = tqdm.tqdm(files_to_merge, leave=False)
        info_list: list[str] = []
        for file_to_merge in merge_bar:
            display_name = file_to_merge.stem[6:]
            was_image = file_to_merge.name[4] == "i"
            status = TEXT().msg_img_2_pdf if was_image else TEXT().msg_pdf_2_pdf
            merge_bar.set_description_str(TEXT().msg_pdf_merging + display_name)
            merger.append(file_to_merge)  # type:ignore
            info_list.append(display_name + status)
        merger.write(output)  # type:ignore
        click.echo(TEXT().msg_post_merge_listing)
        for i in info_list:
            click.echo("  " + i)
        click.echo(f"\n{TEXT().msg_saved_in}{output}")


def process(files: list[Path]):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gather_bar = tqdm.tqdm(enumerate(files), leave=False, total=len(files))
        for index, file in gather_bar:
            original_format_mark = "p" if file.suffix.casefold() == ".pdf" else "i"
            file_temp_path = temp_path.joinpath(f"{index:04}{original_format_mark}_{file.name}").with_suffix(".pdf")
            if file.suffix.casefold() == ".pdf":
                gather_bar.set_description_str(TEXT().msg_file_copying + file.name)
                shutil.copyfile(file, file_temp_path)
            else:
                gather_bar.set_description_str(TEXT().msg_file_converting + file.name)
                convert_image_to_pdf(file, file_temp_path, gather_bar)
        files_to_merge = temp_path.glob("*.*")
        merge_pdf_files(files_to_merge)
    click.echo(TEXT().msg_exit)
