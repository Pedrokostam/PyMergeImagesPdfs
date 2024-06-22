from pathlib import Path
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.

SETUP_ROOT = Path(__file__).parent


def get_from_requirements():
    with open(SETUP_ROOT.joinpath("requirements.txt"), "r", encoding="utf8") as req:
        modules = [x.split("=")[0].lower() for x in req.readlines()]
        return modules


build_options = {
    "packages": get_from_requirements(),
    "excludes": [],
    "include_files": [
        "config_dragdrop.toml",
        "language.json",
    ],
}

base = "console"

executables = [Executable("merge_documents.py", base=base, icon="./icon.ico")]

setup(
    name="Document merger",
    version="1.1",
    description="Merges PDFs, images and document format (MicroSoft office and OpenDocument) into one PDF file.",
    options={"build_exe": build_options},
    executables=executables,
)
