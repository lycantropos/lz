from typing import (Any,
                    Callable)

from hypothesis import given

from lz.functional import (curry)
from lz._core.functional import Curry
from tests import strategies


@given(strategies.callables)
def test_basic(callable_: Callable[..., Any]) -> None:
    result = curry(callable_)

    assert isinstance(result, Curry)
