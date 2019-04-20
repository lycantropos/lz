from hypothesis import given

from lz.functional import flip
from tests import strategies
from tests.hints import FunctionCall
from tests.utils import round_trip_pickle


@given(strategies.transparent_functions_calls)
def test_round_trip(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    flipped = flip(function)

    result = round_trip_pickle(flipped)

    assert result(*args, **kwargs) == flipped(*args, **kwargs)
