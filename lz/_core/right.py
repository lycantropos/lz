from typing import Callable, TypeVar

from reprit import seekers
from reprit.base import generate_repr

from lz._core.functional import ApplierBase
from lz.hints import Range

_Arg = TypeVar('_Arg')
_KwArg = TypeVar('_KwArg')


class Applier(ApplierBase[_Arg, _KwArg, Range]):
    def __init__(self,
                 function: Callable[..., Range],
                 *args: _Arg,
                 **kwargs: _KwArg) -> None:
        super().__init__(function, *args, **kwargs)

    def __call__(self, *args: _Arg, **kwargs: _KwArg) -> Range:
        return self.function(*args, *self.args, **self.kwargs, **kwargs)

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)
