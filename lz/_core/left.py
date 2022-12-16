from typing import Callable, TypeVar

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
        return self.function(self.args, *args, **self.kwargs, **kwargs)
