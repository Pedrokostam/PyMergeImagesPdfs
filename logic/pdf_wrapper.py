import datetime
import io
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Iterable
from PIL import Image
import click
import img2pdf  # type:ignore
import PyPDF2
from natsort import os_sorted
import tqdm

from .configuration import get_page_size, get_text as TEXT, get_output_path


def load_image(image_file_path: Path, *, rotation: float, scale: float, bar: "tqdm.tqdm[Any]", jpeg: bool):
    if scale == 1.0 and rotation == 0.0 and not jpeg:
        # no transformation, no request for jpeg
        return str(image_file_path)
    try:
        image = Image.open(image_file_path)
        is_already_jpeg = isinstance(image.format, str) and image.format.lower() == "jpeg"
        if jpeg and is_already_jpeg and scale == 1.0 and rotation == 0.0:
            # no transformation and already jpeg
            return str(image_file_path)
        if rotation:
            image = image.rotate(rotation, expand=True)
        if scale != 1.0:
            new_size = [int(d * scale) for d in image.size]
            whole_pixel = scale % 2 == 0 or (1 / scale) % 2 == 0
            resample = Image.Resampling.NEAREST if whole_pixel else Image.Resampling.BILINEAR
            image = image.resize(tuple(new_size), resample=resample)
        iob = io.BytesIO()
        image.save(iob, format="JPEG")  # type:ignore
        return iob.getvalue()  # type:ignore
    except ValueError:
        if scale != 1.0 or rotation != 0.0:
            # only an error if there was transformation requested
            # otherwise let img2pdf handle it and any errors
            bar.write(TEXT().msg_transformation_error + image_file_path.name)
        return str(image_file_path)


def get_layout_fun() -> dict[str, Any]:
    size = get_page_size().lower().replace(" ", "").replace("^t", "^T")
    if size == "native":
        return {}
    else:
        size_in_pt = img2pdf.parse_pagesize_rectarg(size)  # type:ignore
        layout_fun = img2pdf.get_layout_fun(size_in_pt)  # type:ignore
        return {"layout_fun": layout_fun}


def convert_image_to_pdf(
    *,
    image_file_path: Path,
    destination_temp_path: Path,
    bar: "tqdm.tqdm[Any]",
    rotation: float,
    scale: float,
    jpeg: bool,
) -> None:
    with open(destination_temp_path, "wb") as pdf_handle:
        layout_fun = get_layout_fun()
        img = load_image(image_file_path=image_file_path, rotation=rotation, scale=scale, bar=bar, jpeg=jpeg)
        try:
            image = img2pdf.convert(img, **layout_fun)  # type:ignore
            pdf_handle.write(image)  # type:ignore
        except ValueError as e:
            bar.write(f"{TEXT().msg_conversion_error}{image_file_path.name} ({e})")
            pdf_handle.close()
            destination_temp_path.unlink(missing_ok=True)


def merge_pdf_files(files_to_merge: Iterable[Path], dry_run: bool):
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
        if not dry_run:
            merger.write(output)  # type:ignore
        click.echo(TEXT().msg_post_merge_listing)
        for i in info_list:
            click.echo("  " + i)
        click.echo(f"\n{TEXT().msg_saved_in}{output}")


def process(files: list[Path], dry_run: bool, rotation: float, scale: float, jpeg: bool):
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
                convert_image_to_pdf(
                    image_file_path=file,
                    destination_temp_path=file_temp_path,
                    bar=gather_bar,
                    rotation=rotation,
                    scale=scale,
                    jpeg=jpeg,
                )
        files_to_merge = temp_path.glob("*.*")
        merge_pdf_files(files_to_merge, dry_run)
    click.echo(TEXT().msg_exit)
