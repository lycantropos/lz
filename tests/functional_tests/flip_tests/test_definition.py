from typing import (Any,
                    Callable,
                    Dict)

from lz.functional import flip
from lz.hints import Domain


def test_basic(transparent_function: Callable[..., Any],
               transparent_function_args: Domain,
               transparent_function_kwargs: Dict[str, Domain]) -> None:
    flipped = flip(transparent_function)

    original_result = transparent_function(*transparent_function_args,
                                           **transparent_function_kwargs)
    flipped_result = flipped(*reversed(transparent_function_args),
                             **transparent_function_kwargs)

    assert flipped_result == original_result
