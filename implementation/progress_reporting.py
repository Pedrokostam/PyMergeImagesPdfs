from typing import Any, Iterable
from tqdm.autonotebook import tqdm

from .logger import get_writer, set_writer


# (self, iterable=None, desc=None, total=None, leave=True, file=None,
#                  ncols=None, mininterval=0.1, maxinterval=10.0, miniters=None,
#                  ascii=None, disable=False, unit='it', unit_scale=False,
#                  dynamic_ncols=False, smoothing=0.3, bar_format=None, initial=0,
#                  position=None, postfix=None, unit_divisor=1000, write_bytes=False,
#                  lock_args=None, nrows=None, colour=None, delay=0.0, gui=False,
#                  **kwargs)


class _TqdmWrapper(tqdm):
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


_BAR: _TqdmWrapper | None = None


def create_progress_bar(iterable: Iterable[Any]):
    global _BAR
    if _BAR:
        _BAR.close()
    _BAR = _TqdmWrapper(
        iterable=iterable,
        mininterval=0.1,
        maxinterval=2,
    )
    return _BAR
