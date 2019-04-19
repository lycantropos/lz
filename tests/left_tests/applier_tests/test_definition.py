from hypothesis import given

from lz import left
from tests.functional_tests import strategies
from tests.utils import PartitionedFunctionCall


@given(strategies.transparent_functions_partitioned_calls)
def test_basic(transparent_function_partitioned_call: PartitionedFunctionCall
               ) -> None:
    (function,
     (first_args_part,
      second_args_part),
     (first_kwargs_part,
      second_kwargs_part)) = transparent_function_partitioned_call

    result = left.applier(function,
                          *first_args_part,
                          **first_kwargs_part)

    assert callable(result)
    assert (result(*second_args_part,
                   **second_kwargs_part)
            == function(*first_args_part, *second_args_part,
                        **first_kwargs_part, **second_kwargs_part))
