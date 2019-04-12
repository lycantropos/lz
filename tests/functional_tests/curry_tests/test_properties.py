from typing import (Callable,
                    Dict,
                    Tuple)

import pytest

from lz.functional import (Curry,
                           curry)
from lz.hints import (Domain,
                      Range)


def test_empty_call(transparent_function: Callable[..., Range]) -> None:
    curried = curry(transparent_function)

    result = curried()

    assert curried.signature.all_set() or isinstance(result, Curry)


def test_valid_call(transparent_function: Callable[..., Range],
                    transparent_function_args: Tuple[Domain, ...],
                    transparent_function_kwargs: Dict[str, Domain]) -> None:
    curried = curry(transparent_function)

    result = curried(*transparent_function_args, **transparent_function_kwargs)

    assert result == transparent_function(*transparent_function_args,
                                          **transparent_function_kwargs)


def test_consecutive_call(transparent_function: Callable[..., Range],
                          transparent_function_args: Tuple[Domain, ...],
                          transparent_function_kwargs: Dict[str, Domain]
                          ) -> None:
    curried = curry(transparent_function)
    double_curried = curry(curried)

    result = double_curried(*transparent_function_args,
                            **transparent_function_kwargs)

    assert result == curried(*transparent_function_args,
                             **transparent_function_kwargs)


def test_invalid_args_call(
        non_variadic_transparent_function: Callable[..., Range],
        non_variadic_transparent_function_invalid_args: Tuple[Domain, ...],
        non_variadic_transparent_function_kwargs: Dict[str, Domain]) -> None:
    curried = curry(non_variadic_transparent_function)

    with pytest.raises(TypeError):
        curried(*non_variadic_transparent_function_invalid_args,
                **non_variadic_transparent_function_kwargs)


def test_invalid_kwargs_call(
        non_variadic_transparent_function: Callable[..., Range],
        non_variadic_transparent_function_args: Dict[str, Domain],
        non_variadic_transparent_function_invalid_kwargs: Tuple[Domain, ...]
) -> None:
    curried = curry(non_variadic_transparent_function)

    with pytest.raises(TypeError):
        curried(*non_variadic_transparent_function_args,
                **non_variadic_transparent_function_invalid_kwargs)
