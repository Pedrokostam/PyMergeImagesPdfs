import datetime
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Iterable
import click
import PyPDF2
import tempfile
import img2pdf


def load_config():
    program_folder = Path(globals().get('__file__', sys.argv[0])).parent
    jayson = list(program_folder.glob('config.json'))
    if not jayson:
        return Path('.')
    else:
        with open(jayson[0], mode='r') as jj:
            data = json.load(jj)
            str_path = data.get('output_path', '.')
            str_path = os.path.expanduser(str_path)
            str_path = os.path.expandvars(str_path)
            return Path(str_path)


def glob_source(path: Path) -> set[Path]:
    files: list[Path] = []
    patterns = ['*.pdf', '*.png', '*.jpg', '*.bmp', '*.jpeg', '*.tif', '*.tiff']
    for pattern in patterns:
        files.extend(path.rglob(pattern))
    return set(files)


def process(files: Iterable[Path], output_dir: Path):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for index, file in enumerate(files):
            file_temp_path = temp_path.joinpath(f'{index:02}_{file.name}').with_suffix('.pdf')
            if file.match('*.pdf'):
                shutil.copyfile(file, file_temp_path)
            else:
                a4_in_pt = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
                layout_fun = img2pdf.get_layout_fun(a4_in_pt)
                with open(file_temp_path, 'wb') as pdf_path, open(file) as img:
                    pdf_path.write(img2pdf.convert(str(file), layout_fun=layout_fun))
        with PyPDF2.PdfMerger() as merger:
            to_merge = sorted(Path(temp_dir).glob('*.*'))
            date_now = datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')
            output = output_dir.joinpath(f'scalony {date_now}.pdf')
            print()
            for tm in to_merge:
                merger.append(tm)
                print(f'Dołączono: {tm.stem}')
            merger.write(output)
            print(f'\nZapisano scalony plik w {output}')


@click.command()
@click.argument('paths', required=False, nargs=-1,
                type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, writable=False,
                                resolve_path=True, path_type=Path))
def merge(paths: tuple[Path]):
    files: set[Path] = set([])
    ext = ['.pdf', '.png', '.jpg', '.bmp', '.jpeg', '.tif', '.tiff']
    if not paths:
        files = glob_source(Path(os.getcwd()))
    else:
        for path in paths:
            if path.is_file():
                files.add(path)
            else:
                files = files.union(glob_source(path))
    files = set((x for x in files if x.suffix in ext))
    if not files:
        print('Brak plików do scalenia!')
        input('\nWciśnij ENTER, aby wyjść')
        return
    files_sorted = sorted(files)
    print('Scalam następujące pliki:', *files_sorted, sep='\n\t')
    process(files_sorted, load_config())
    input('Wciśnij ENTER, aby wyjść')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    merge()
