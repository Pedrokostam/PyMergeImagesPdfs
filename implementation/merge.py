import subprocess
import tempfile
import os
from pathlib import Path
from time import sleep
from typing import Sequence
import pymupdf

from .progress_reporting import close_progress_bar, create_progress_bar
from .configuration import Configuration
from .logger import print_newline, print_translated, translate
from .dimension import Dimension
from .files import is_image_extension, is_pdf_extension, is_document_extension

PathLike = str | Path


# .\soffice.exe --convert-to pdf 'PATH' --outdir 'DIR'
def libre_to_pdf(document_path: Path, config: Configuration, output_file: pymupdf.Document, dry_run: bool):
    if not config.libreoffice_path:
        print_translated("LibreMissing", document_path)
        return
    if dry_run:
        return
    tempdir = Path(tempfile.gettempdir()).joinpath("Zszywacz")
    os.makedirs(tempdir, exist_ok=True)
    subprocess.run(
        [config.libreoffice_path, "--convert-to", "pdf", str(document_path), "--outdir", tempdir], check=True
    )
    output_file.insert_file(
        tempdir.joinpath(document_path.with_suffix(".pdf").name)
    )  # insert_file can handle pathlib.Path


def merge_documents(files: Sequence[PathLike], output_path: Path, config: Configuration):
    print_newline()
    all_filepaths = [Path(x) for x in files]
    pdf_filepaths = [x for x in all_filepaths if is_pdf_extension(x)]
    output_file = pymupdf.Document()
    actual_pagesize = config.image_page_fallback_size.rect
    if pdf_filepaths and not config.force_image_page_fallback_size:
        first_doc = pymupdf.open(pdf_filepaths[0])
        actual_pagesize = first_doc.load_page(0).rect
        dim = Dimension(actual_pagesize.width, actual_pagesize.height, "pt")
        print_translated("FirstPageSize", dim)
        print_newline()
    progress_bar = create_progress_bar(all_filepaths, desc=translate("Merging", 0))
    for file in progress_bar:
        progress_bar.set_description(translate("Merging", output_file.page_count))
        if is_pdf_extension(file):
            output_file.insert_file(file)
        elif is_image_extension(file):
            image_to_pdf(file, config, output_file, actual_pagesize)
        elif is_document_extension(file):
            libre_to_pdf(file, config, output_file, dry_run=config.what_if)
        else:
            print_translated("UnknownFileType", file)
        print_translated("MergedFile", file)
    close_progress_bar()
    print_translated("MergingFinished", output_file.page_count)
    output_path = output_path.with_suffix(".pdf")  # Make sure PDF is the extension
    if not config.what_if:
        output_file.save(output_path)  # save can handle pathlib.Path
    print_newline()
    print_translated("OutputSaved", output_path.absolute())


def image_to_pdf(file, config, output_file, actual_pagesize):
    img = pymupdf.open(file)
    img_pdf_bytes = img.convert_to_pdf()
    img.close()
    img_pdf = pymupdf.open("pdf", img_pdf_bytes)
    new_page = output_file.new_page(width=actual_pagesize.width, height=actual_pagesize.height)
    margined_rect = (-config.margin + new_page.rect).rect
    new_page.show_pdf_page(margined_rect, img_pdf, pno=0, keep_proportion=True, rotate=0)
