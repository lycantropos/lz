from typing import (Callable,
                    Dict,
                    Tuple)

from lz import left
from lz.hints import (Domain,
                      Range)


def test_basic(transparent_function: Callable[..., Range],
               transparent_function_args: Tuple[Domain, ...],
               transparent_function_first_args_part: Tuple[Domain, ...],
               transparent_function_second_args_part: Tuple[Domain, ...],
               transparent_function_kwargs: Dict[str, Domain],
               transparent_function_first_kwargs_part: Dict[str, Domain],
               transparent_function_second_kwargs_part: Dict[str, Domain]
               ) -> None:
    result = left.applier(transparent_function,
                          *transparent_function_first_args_part,
                          **transparent_function_first_kwargs_part)

    assert callable(result)
    assert (result(*transparent_function_second_args_part,
                   **transparent_function_second_kwargs_part)
            == transparent_function(*transparent_function_args,
                                    **transparent_function_kwargs))
