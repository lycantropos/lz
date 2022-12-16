import pytest
from hypothesis import given

from lz import left
from lz.functional import curry
from tests import strategies
from tests.hints import (FunctionCall,
                         PartitionedFunctionCall)


@given(strategies.partitioned_transparent_functions_calls)
def test_basic(partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call
    applied = left.applier(function, *first_args_part, **first_kwargs_part)

    result = curry(applied)

    assert (result(*second_args_part, **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))


@given(strategies.non_variadic_transparent_functions_calls_with_invalid_args)
def test_invalid_args(function_call: FunctionCall) -> None:
    function, invalid_args, kwargs = function_call
    applied = left.applier(function, *invalid_args, **kwargs)

    with pytest.raises(TypeError):
        curry(applied)


@given(strategies.non_variadic_transparent_functions_calls_with_invalid_kwargs)
def test_invalid_kwargs(function_call: FunctionCall) -> None:
    function, args, invalid_kwargs = function_call
    applied = left.applier(function, *args, **invalid_kwargs)

    with pytest.raises(TypeError):
        curry(applied)
