import pytest
from hypothesis import given

from lz._core.functional import Curry
from lz._core.signatures import to_signature
from lz.functional import curry
from tests import strategies
from tests.hints import (Function,
                         FunctionCall)


@given(strategies.transparent_functions)
def test_empty_call(function: Function) -> None:
    curried = curry(function)

    result = curried()

    assert to_signature(curried).all_set() or isinstance(result, Curry)


@given(strategies.transparent_functions_calls)
def test_valid_call(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call

    curried = curry(function)

    result = curried(*args, **kwargs)

    assert result == function(*args, **kwargs)


@given(strategies.transparent_functions_calls)
def test_involution(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    double_curried = curry(curry(function))

    result = double_curried(*args, **kwargs)

    assert result == function(*args, **kwargs)


@given(strategies.non_variadic_transparent_functions_calls_with_invalid_args)
def test_invalid_args_call(
        function_call_with_invalid_args: FunctionCall
) -> None:
    function, invalid_args, kwargs = function_call_with_invalid_args
    curried = curry(function)

    with pytest.raises(TypeError):
        curried(*invalid_args, **kwargs)


@given(strategies.non_variadic_transparent_functions_calls_with_invalid_kwargs)
def test_invalid_kwargs_call(
        function_call_with_invalid_kwargs: FunctionCall
) -> None:
    function, args, invalid_kwargs = function_call_with_invalid_kwargs
    curried = curry(function)

    with pytest.raises(TypeError):
        curried(*args, **invalid_kwargs)
