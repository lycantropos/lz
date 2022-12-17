from typing import (Callable,
                    TypeVar)

from typing_extensions import final

from lz._core.functional import ApplierBase
from lz._core.signatures import (Signature,
                                 to_signature)

_Arg = TypeVar('_Arg')
_KwArg = TypeVar('_KwArg')
_Result = TypeVar('_Result')


@final
class Applier(ApplierBase[_Arg, _KwArg, _Result]):
    def __init__(self,
                 function: Callable[..., _Result],
                 *args: _Arg,
                 **kwargs: _KwArg) -> None:
        super().__init__(function, *args, **kwargs)

    def __call__(self, *args: _Arg, **kwargs: _KwArg) -> _Result:
        return self.function(*self.args, *args, **self.kwargs, **kwargs)


@to_signature.register(Applier)
def _(_value: Applier) -> Signature:
    return to_signature(_value.function).bind(*_value.args, **_value.kwargs)
