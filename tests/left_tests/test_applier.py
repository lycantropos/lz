from typing import (Callable,
                    Dict,
                    Tuple)

from lz import left
from lz.hints import (Domain,
                      Range)


def test_basic(transparent_function: Callable[..., Range],
               transparent_function_args: Tuple[Domain, ...],
               transparent_function_applied_args: Tuple[Domain, ...],
               transparent_function_rest_args: Tuple[Domain, ...],
               transparent_function_kwargs: Dict[str, Domain],
               transparent_function_applied_kwargs: Dict[str, Domain],
               transparent_function_rest_kwargs: Dict[str, Domain]) -> None:
    applied = left.applier(transparent_function,
                           *transparent_function_applied_args,
                           **transparent_function_applied_kwargs)

    result = applied(*transparent_function_rest_args,
                     **transparent_function_rest_kwargs)

    assert result == transparent_function(*transparent_function_args,
                                          **transparent_function_kwargs)
