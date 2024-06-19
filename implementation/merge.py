from .logger import printline, printlog
from .dimension import Dimension
from .files import is_image_extension, is_pdf_extension, is_document_extension
from pathlib import Path
from typing import Sequence
from .configuration import Configuration
import pymupdf
import subprocess
import tempfile
import os

PathLike = str | Path


# .\soffice.exe --convert-to pdf 'PATH' --outdir 'DIR'
def libre_to_pdf(document_path: Path, config: Configuration, output_file: pymupdf.Document):
    if not config.libreoffice_path:
        printlog("LibreMissing", document_path)
        return
    tempdir = Path(tempfile.gettempdir()).joinpath("Zszywacz")
    os.makedirs(tempdir, exist_ok=True)
    subprocess.run([config.libreoffice_path, "--convert-to", "pdf", str(document_path), "--outdir", tempdir])
    output_file.insert_file(
        tempdir.joinpath(document_path.with_suffix(".pdf").name)
    )  # insert_file can handle pathlib.Path


def merge_documents(files: Sequence[PathLike], output_path: Path, config: Configuration):
    all_filepaths = [Path(x) for x in files]
    pdf_filepaths = [x for x in all_filepaths if is_pdf_extension(x)]
    output_file = pymupdf.Document()
    actual_pagesize = config.image_page_fallback_size.rect
    if pdf_filepaths and not config.force_image_page_fallback_size:
        first_doc = pymupdf.open(pdf_filepaths[0])
        actual_pagesize = first_doc.load_page(0).rect
        dim = Dimension(actual_pagesize.width, actual_pagesize.height, "pt")
        printlog("FirstPageSize", dim)
        printline()
    for file in all_filepaths:
        printlog("Stitching", file)
        if is_pdf_extension(file):
            output_file.insert_file(file)
        elif is_image_extension(file):
            image_to_pdf(file, config, output_file, actual_pagesize)
        elif is_document_extension(file):
            libre_to_pdf(file, config, output_file)
        else:
            printlog("UnknownFileType", file)
    output_file.save(output_path)  # save can handle pathlib.Path
    printline()
    printlog("OutputSaved", output_path.absolute())


def image_to_pdf(file, config, output_file, actual_pagesize):
    img = pymupdf.open(file)
    img_pdf_bytes = img.convert_to_pdf()
    img.close()
    img_pdf = pymupdf.open("pdf", img_pdf_bytes)
    new_page = output_file.new_page(width=actual_pagesize.width, height=actual_pagesize.height)
    margined_rect = (-config.margin + new_page.rect).rect
    new_page.show_pdf_page(margined_rect, img_pdf, pno=0, keep_proportion=True, rotate=0)
