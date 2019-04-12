from typing import (Callable,
                    Dict,
                    Tuple)

from lz.functional import pack
from lz.hints import (Domain,
                      Range)
from tests.utils import round_trip_pickle


def test_round_trip(transparent_function: Callable[..., Range],
                    transparent_function_args: Tuple[Domain, ...],
                    transparent_function_kwargs: Dict[str, Domain]) -> None:
    packed = pack(transparent_function)

    result = round_trip_pickle(packed)

    assert (result(transparent_function_args, transparent_function_kwargs)
            == packed(transparent_function_args, transparent_function_kwargs))
