from typing import (Callable,
                    Dict,
                    Tuple)

from lz import (left,
                right)
from lz.functional import curry
from lz.hints import (Domain,
                      Range)


def test_consecutive_application(
        transparent_function: Callable[..., Range],
        transparent_function_args: Tuple[Domain, ...],
        transparent_function_first_args_part: Tuple[Domain, ...],
        transparent_function_second_args_part: Tuple[Domain, ...],
        transparent_function_kwargs: Dict[str, Domain],
        transparent_function_first_kwargs_part: Dict[str, Domain],
        transparent_function_second_kwargs_part: Dict[str, Domain]) -> None:
    fold = left.folder(left.applier,
                       left.applier(transparent_function,
                                    **transparent_function_first_kwargs_part))
    result = fold(transparent_function_first_args_part)

    assert callable(result)
    assert (result(*transparent_function_second_args_part,
                   **transparent_function_second_kwargs_part)
            == transparent_function(*transparent_function_args,
                                    **transparent_function_kwargs))


def test_composition_with_right(
        transparent_function: Callable[..., Range],
        transparent_function_args: Tuple[Domain, ...],
        transparent_function_first_args_part: Tuple[Domain, ...],
        transparent_function_second_args_part: Tuple[Domain, ...],
        transparent_function_kwargs: Dict[str, Domain],
        transparent_function_first_kwargs_part: Dict[str, Domain],
        transparent_function_second_kwargs_part: Dict[str, Domain]) -> None:
    right_applied = right.applier(transparent_function,
                                  *transparent_function_second_args_part,
                                  **transparent_function_first_kwargs_part)
    result = left.applier(right_applied,
                          *transparent_function_first_args_part,
                          **transparent_function_second_kwargs_part)

    assert callable(result)
    assert result() == transparent_function(*transparent_function_args,
                                            **transparent_function_kwargs)


def test_currying(transparent_function: Callable[..., Range],
                  transparent_function_args: Tuple[Domain, ...],
                  transparent_function_first_args_part: Tuple[Domain, ...],
                  transparent_function_second_args_part: Tuple[Domain, ...],
                  transparent_function_kwargs: Dict[str, Domain],
                  transparent_function_first_kwargs_part: Dict[str, Domain],
                  transparent_function_second_kwargs_part: Dict[str, Domain]
                  ) -> None:
    applied = left.applier(transparent_function,
                           *transparent_function_first_args_part,
                           **transparent_function_first_kwargs_part)

    result = curry(applied)

    assert (result(*transparent_function_second_args_part,
                   **transparent_function_second_kwargs_part)
            == transparent_function(*transparent_function_args,
                                    **transparent_function_kwargs))
