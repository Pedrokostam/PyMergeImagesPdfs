from typing import Iterable, TypeVar
from tqdm.autonotebook import tqdm

from .logger import get_writer, set_writer


# (self, iterable=None, desc=None, total=None, leave=True, file=None,
#        ncols=None, mininterval=0.1, maxinterval=10.0, miniters=None,
#        ascii=None, disable=False, unit='it', unit_scale=False,
#        dynamic_ncols=False, smoothing=0.3, bar_format=None, initial=0,
#        position=None, postfix=None, unit_divisor=1000, write_bytes=False,
#        lock_args=None, nrows=None, colour=None, delay=0.0, gui=False,
#        **kwargs)

T = TypeVar("T")


class __TqdmWrapper(tqdm):
    def __init__(self, **kwargs):
        """
        DO NOT INSTANTIATE IT MANUALLY

        CALL create_progress_bar(iterable)
        """
        super().__init__(**kwargs)
        set_writer(self)

    def close(self):
        if get_writer() is self:
            set_writer(None)
        super().close()


__BAR: __TqdmWrapper | None | tqdm = None


def create_progress_bar(iterable: Iterable[T] | None, desc: str | None = None):
    global __BAR  # pylint: disable=global-statement
    if __BAR:
        __BAR.close()
    __BAR = tqdm(
        iterable=iterable,
        mininterval=0.1,
        desc=desc,
        maxinterval=2,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        leave=False,
    )
    set_writer(__BAR)
    return __BAR


def close_progress_bar():
    if __BAR:
        __BAR.close()
    set_writer(None)
