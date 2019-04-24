from hypothesis import given

from lz.functional import pack
from tests import strategies
from tests.hints import FunctionCall


@given(strategies.transparent_functions_calls)
def test_basic(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    packed = pack(function)

    result = packed(args, kwargs)

    assert result == function(*args, **kwargs)
