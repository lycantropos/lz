from hypothesis import given

from lz.functional import flip
from tests import strategies
from tests.hints import FunctionCall


@given(strategies.transparent_functions_calls)
def test_basic(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    flipped = flip(function)

    original_result = function(*args, **kwargs)
    flipped_result = flipped(*reversed(args), **kwargs)

    assert flipped_result == original_result
