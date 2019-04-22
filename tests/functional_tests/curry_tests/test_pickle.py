from hypothesis import given

from lz.functional import curry
from tests import strategies
from tests.hints import FunctionCall
from tests.utils import (round_trip_pickle,
                         slow_data_generation)


@slow_data_generation
@given(strategies.transparent_functions_calls)
def test_round_trip(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    curried = curry(function)

    result = round_trip_pickle(curried)

    assert result(*args, **kwargs) == curried(*args, **kwargs)
