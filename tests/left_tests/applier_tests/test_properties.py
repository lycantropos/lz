from hypothesis import given

from lz import (left,
                right)
from lz.functional import curry
from tests import strategies
from tests.hints import PartitionedFunctionCall


@given(strategies.partitioned_transparent_functions_calls)
def test_consecutive_application(
        partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call

    fold = left.folder(left.applier,
                       left.applier(function,
                                    **first_kwargs_part))
    result = fold(first_args_part)

    assert callable(result)
    assert (result(*second_args_part, **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))


@given(strategies.partitioned_transparent_functions_calls)
def test_composition_with_right(
        partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call
    right_applied = right.applier(function,
                                  *second_args_part,
                                  **first_kwargs_part)

    result = left.applier(right_applied,
                          *first_args_part,
                          **second_kwargs_part)

    assert callable(result)
    assert result() == function(*first_args_part, *second_args_part,
                                **first_kwargs_part, **second_kwargs_part)


@given(strategies.partitioned_transparent_functions_calls)
def test_currying(partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call
    applied = left.applier(function,
                           *first_args_part,
                           **first_kwargs_part)

    result = curry(applied)

    assert (result(*second_args_part, **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))
