from hypothesis import given

from lz import right
from tests import strategies
from tests.hints import PartitionedFunctionCall
from tests.utils import round_trip_pickle


@given(strategies.partitioned_transparent_functions_calls)
def test_basic(partitioned_function_call: PartitionedFunctionCall) -> None:
    (function,
     (first_args_part, second_args_part),
     (first_kwargs_part, second_kwargs_part)) = partitioned_function_call
    applied = right.applier(function, *second_args_part, **first_kwargs_part)

    result = round_trip_pickle(applied)

    assert (result(*first_args_part, **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))
