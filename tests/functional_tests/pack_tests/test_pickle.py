from hypothesis import given

from lz.functional import pack
from tests import strategies
from tests.utils import (FunctionCall,
                         round_trip_pickle)


@given(strategies.transparent_functions_calls)
def test_round_trip(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    packed = pack(function)

    result = round_trip_pickle(packed)

    assert result(args, kwargs) == packed(args, kwargs)
