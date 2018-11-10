from typing import (Callable,
                    Dict,
                    Tuple)

from lz import right, left
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
    applied = right.applier(transparent_function,
                            *reversed(transparent_function_second_args_part),
                            **transparent_function_first_kwargs_part)

    result = applied(*transparent_function_first_args_part,
                     **transparent_function_second_kwargs_part)

    assert result == transparent_function(*transparent_function_args,
                                          **transparent_function_kwargs)


def test_consecutive_application(
        transparent_function: Callable[..., Range],
        transparent_function_args: Tuple[Domain, ...],
        transparent_function_first_args_part: Tuple[Domain, ...],
        transparent_function_second_args_part: Tuple[Domain, ...],
        transparent_function_kwargs: Dict[str, Domain],
        transparent_function_first_kwargs_part: Dict[str, Domain],
        transparent_function_second_kwargs_part: Dict[str, Domain]) -> None:
    fold = left.folder(right.applier,
                       right.applier(transparent_function,
                                     **transparent_function_first_kwargs_part))
    applied = fold(reversed(transparent_function_second_args_part))

    result = applied(*transparent_function_first_args_part,
                     **transparent_function_second_kwargs_part)

    assert result == transparent_function(*transparent_function_args,
                                          **transparent_function_kwargs)
