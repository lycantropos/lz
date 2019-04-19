from hypothesis import given

from lz.functional import (curry,
                           flip)
from tests import strategies
from tests.utils import FunctionCall


@given(strategies.transparent_functions_calls)
def test_involution(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    double_flipped = flip(flip(function))

    original_result = function(*args, **kwargs)
    double_flipped_result = double_flipped(*args, **kwargs)

    assert double_flipped_result == original_result


@given(strategies.transparent_functions_calls)
def test_currying(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    flipped = flip(function)
    curried_flipped = curry(flipped)

    result = curried_flipped(*args, **kwargs)

    assert result == flipped(*args, **kwargs)
