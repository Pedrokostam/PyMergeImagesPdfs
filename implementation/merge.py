from .files import is_image_extension, is_pdf_extension
from pathlib import Path
from typing import Sequence
from .config import Config
import pymupdf
import subprocess
import tempfile
import os

PathLike = str | Path


    # .\soffice.exe --convert-to pdf 'PATH' --outdir 'DIR'
def libre_to_pdf(document_path: Path, config: Config, output_file: pymupdf.Document):
    if not config.libreoffice_path:
        return
    tempdir = Path(tempfile.gettempdir()).joinpath("Zszywacz")
    os.makedirs(tempdir, exist_ok=True)
    subprocess.run([config.libreoffice_path, "--convert-to", "pdf", str(document_path), "--outdir", tempdir])
    output_file.insert_file(str(tempdir.joinpath(document_path.name)))


def merge(files: Sequence[PathLike], working_dir: Path, config: Config):
    all_filepaths = [Path(x) for x in files]
    pdf_filepaths = [x for x in all_filepaths if is_pdf_extension(x)]
    output = config.output_folder_expanded(working_dir)
    output_file = pymupdf.Document()
    actual_pagesize = config.page_size.rect
    if pdf_filepaths:
        first_doc = pymupdf.open(pdf_filepaths[0])
        actual_pagesize = first_doc.load_page(0).rect
    for file in all_filepaths:
        print(f"Zszywanie: {file}")
        if is_pdf_extension(file):
            output_file.insert_file(str(file))
        elif is_image_extension(file):
            image_to_pdf(config, output_file, actual_pagesize, file)
        elif config.libreoffice_path:
            libre_to_pdf(file, config, output_file)
        else:
            print(f"Unknown file type: {file}")
    output_file.save(str(output))
    print(f"Zapisano w {output}")

def image_to_pdf(config, output_file, actual_pagesize, file):
    img = pymupdf.open(file)
    img_pdf_bytes = img.convert_to_pdf()
    img.close()
    img_pdf = pymupdf.open("pdf", img_pdf_bytes)
    new_page = output_file.new_page(width=actual_pagesize.width, height=actual_pagesize.height)  # type: ignore
    margined_rect = (new_page.rect - config.margin).rect
    new_page.show_pdf_page(margined_rect, img_pdf, pno=0, keep_proportion=True, rotate=0)
