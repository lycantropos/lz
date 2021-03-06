from hypothesis import given

from lz import (left,
                right)
from tests import strategies
from tests.hints import PartitionedFunctionCall


@given(strategies.partitioned_transparent_functions_calls)
def test_consecutive_application(
        partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call
    fold = left.folder(right.applier,
                       right.applier(function,
                                     **first_kwargs_part))

    result = fold(second_args_part)

    assert callable(result)
    assert (result(*first_args_part, **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))


@given(strategies.partitioned_transparent_functions_calls)
def test_composition_with_left(
        partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call
    left_applied = left.applier(function,
                                *first_args_part,
                                **first_kwargs_part)

    result = right.applier(left_applied,
                           *second_args_part,
                           **second_kwargs_part)

    assert callable(result)
    assert result() == function(*first_args_part, *second_args_part,
                                **first_kwargs_part, **second_kwargs_part)
