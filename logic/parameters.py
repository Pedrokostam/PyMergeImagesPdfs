# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportGeneralTypeIssues=false
# pyright: reportMissingTypeStubs=false
from argparse import Namespace
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from typing import Any, Callable
import img2pdf
import toml
from .translator import TRANSLATOR as T

PROGRAM_FOLDER = Path(globals().get("__file__", sys.argv[0])).parent.parent
CONFIG_PATH = PROGRAM_FOLDER.joinpath("config.toml")
DEFAULT_PARAMETERS: dict[str, Any] = {
    "force": True,
    "output_file": None,
    "output_directory": ".",
    "rotate": None,
    "bordersize": None,
    "imagesize": None,
    "pagesize": "A4",
    "whatif": True,
    "language": "en",
    "rotation": "0",
    "autoorient": False,
}
PARAMETERS = DEFAULT_PARAMETERS.copy()
DEFAULT_ARGS = [
    "pagesize",
    "language",
    "output_directory",
    "rotate",
    "imagesize",
    "bordersize",
    "force",
    "whatif",
    "output_file",
]


def save_config(namespace: SimpleNamespace | Namespace):
    dict_pars = vars(namespace)
    to_save = {key: dict_pars[key] for key in DEFAULT_ARGS if key in dict_pars}
    with open(CONFIG_PATH, "w") as config_handle:
        toml.dump(to_save, config_handle)
    print(T.get("tln_config_saved", path=CONFIG_PATH))
    print(toml.dumps(to_save))


def update_config_dict(new_dict: dict[str, Any]):
    for key in new_dict.keys():
        PARAMETERS[key] = new_dict[key]


def load_config():
    if not CONFIG_PATH.exists():
        print("No config file")
    else:
        try:
            with open(CONFIG_PATH, mode="r") as config_handle:
                configuration_dict = toml.load(config_handle)
                update_config_dict(configuration_dict)
        except toml.decoder.TomlDecodeError:
            print("Invalid config file!")


def parse_size(size: str) -> str:
    return size.lower().replace(" ", "").replace("^t", "^T")


def parse_pagesize(pagesize: str) -> tuple[float, float]:
    return img2pdf.parse_pagesize_rectarg(parse_size(pagesize))


def parse_imgsize(imgsize: str, pagesize: tuple[float, float] | None) -> tuple[float, float]:
    size = parse_imgborder_size(imgsize, pagesize)
    return img2pdf.parse_imgsize_rectarg(size)


def parse_imgborder_size(imgsize: str, pagesize: tuple[float, float] | None):
    size = parse_size(imgsize)
    i = 0
    while True:
        m = re.search(r"(?P<all>(?P<num>[\d\.,]+)%)", size)
        if pagesize is None:
            raise ValueError("Percent based dimension cannot be used while pagesize is None")
        if not m:
            break
        float_str: str = m["num"]
        percentage = float(float_str)
        actualsize = percentage * pagesize[i]
        repl = m["all"]
        size = size.replace(repl, f"{actualsize:.3f}")
        i += 1
    return size


def parse_bordersize(bordersize: str, pagesize: tuple[float, float] | None) -> tuple[float, float]:
    size = parse_imgborder_size(bordersize, pagesize)
    return img2pdf.parse_borderarg(size)


def get_layout_function(
    pagesize: str | None,
    imgsize: str | None,
    bordersize: str | None,
    autoorient: Any,
) -> Callable[..., tuple[Any]]:
    page_t = parse_pagesize(pagesize) if pagesize else None
    img_t = parse_bordersize(bordersize, page_t) if imgsize else None
    border_t = parse_bordersize(img_t, page_t) if bordersize else None
    orient_t = bool(autoorient)
    lay_fun = img2pdf.get_layout_fun(
        pagesize=page_t,
        imgsize=img_t,
        border=border_t,
        auto_orient=orient_t,
    )
    return lay_fun


# class Parameters:
#     def __init__(self) -> None:
#         self.rotation: img2pdf.Rotation = img2pdf.Rotation.none
#         self.scale
#         pass
if __name__ == "__main__":
    p = parse_pagesize("a5")
    b = parse_bordersize("15%:31%", p)
    print(b)
    p = parse_pagesize("a0")
    b = parse_bordersize("15%:31%", p)
    print(b)
