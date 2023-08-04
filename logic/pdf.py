# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportGeneralTypeIssues=false
# pyright: reportMissingTypeStubs=false
from pathlib import Path
import re
from typing import Any, Callable
import img2pdf  # type:ignore
import pypdf


def parse_size(size: str) -> str:
    return size.lower().replace(" ", "").replace("^t", "^T")


def arg_is_none(x: str | None):
    return x is None or re.search(r"(none|null)", x, flags=re.RegexFlag.IGNORECASE) or not re.search(r"[\d\w]+", x)


def parse_pagesize(pagesize: str | None) -> tuple[float, float] | None:
    if arg_is_none(pagesize):
        return None
    return img2pdf.parse_pagesize_rectarg(parse_size(pagesize))


def parse_imgsize(imgsize: str | None, pagesize: tuple[float, float] | None) -> tuple[float, float]:
    if arg_is_none(imgsize):
        return None
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


def parse_bordersize(bordersize: str | None, pagesize: tuple[float, float] | None) -> tuple[float, float]:
    if arg_is_none(bordersize):
        return None
    size = parse_imgborder_size(bordersize, pagesize)
    return img2pdf.parse_borderarg(size)


def get_parameters(
    paths: list[Path],
    rotation: str | None,
    pagesize: str | None,
    imagesize: str | None,
    bordersize: str | None,
    autoorient: bool,
    **kwargs: str,
) -> dict[str, Any]:
    pagesize_t: tuple[float, float] | None = parse_pagesize(pagesize)
    if not pagesize_t:
        pagesize_t = get_first_pdf_size(paths)
    rot = img2pdf.Rotation[rotation.lower()] if rotation else None
    if pagesize_t and (rot == img2pdf.Rotation["270"] or rot == img2pdf.Rotation["90"]):
        pagesize_t = pagesize_t[1], pagesize_t[0]
    layout_fun: Callable[..., tuple[Any]] = img2pdf.get_layout_fun(
        pagesize=pagesize_t,
        imgsize=parse_imgsize(imagesize, pagesize_t),
        border=parse_bordersize(bordersize, pagesize_t),
    )
    return {
        "layout_fun": layout_fun,
        "rotation": rot,
        "pagesize": pagesize_t,
        "autoorient": autoorient,
    }


def get_first_pdf_size(paths: list[Path]) -> tuple[float, float] | None:
    for p in paths:
        if p.suffix.casefold() == ".pdf":
            reader = pypdf.PdfReader(p)
            box = reader.pages[0].mediabox
            pagesize_t: tuple[float, float] = box.width, box.height
            return pagesize_t
    return None


def convert_image(
    image: Path,
    rotation: img2pdf.Rotation,
    layout_fun: Callable[..., tuple[Any]],
    **kwargs: str,
):
    image_bytes = img2pdf.convert(
        str(image),
        rotation=rotation,
        layout_fun=layout_fun,
    )
    return image_bytes
