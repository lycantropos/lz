from hypothesis import given

from lz import left
from tests.functional_tests import strategies
from tests.utils import (PartitionedFunctionCall,
                         round_trip_pickle)


@given(strategies.transparent_functions_partitioned_calls)
def test_basic(transparent_function_partitioned_call: PartitionedFunctionCall
               ) -> None:
    (function,
     (first_args_part,
      second_args_part),
     (first_kwargs_part,
      second_kwargs_part)) = transparent_function_partitioned_call
    applied = left.applier(function, *first_args_part, **first_kwargs_part)

    result = round_trip_pickle(applied)

    assert (result(*second_args_part, **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))
