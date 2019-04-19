from hypothesis import given

from lz.functional import (curry,
                           pack)
from tests import strategies
from tests.utils import FunctionCall


@given(strategies.transparent_functions_calls)
def test_currying(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    packed = pack(function)
    curried_packed = curry(packed)

    result = curried_packed(args,
                            kwargs)

    assert result == packed(args,
                            kwargs)
