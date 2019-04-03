from typing import (Callable,
                    Dict,
                    Tuple)

from lz.functional import curry
from lz.hints import (Domain,
                      Range)
from tests.utils import round_trip_pickle


def test_round_trip(transparent_function: Callable[..., Range],
                    transparent_function_args: Tuple[Domain, ...],
                    transparent_function_kwargs: Dict[str, Domain]) -> None:
    curried = curry(transparent_function)

    result = round_trip_pickle(curried)

    assert (result(*transparent_function_args,
                   **transparent_function_kwargs)
            == curried(*transparent_function_args,
                       **transparent_function_kwargs))
