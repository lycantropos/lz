from hypothesis import given

from lz import right
from tests import strategies
from tests.utils import PartitionedFunctionCall


@given(strategies.partitioned_transparent_functions_calls)
def test_basic(partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call

    result = right.applier(function, *second_args_part, **first_kwargs_part)

    assert callable(result)
    assert (result(*first_args_part, **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))
