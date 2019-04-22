from hypothesis import given

from lz.sorting import (Implementation,
                        implementations,
                        register_implementation)
from . import strategies


@given(strategies.unregistered_sorting_algorithms,
       strategies.sorting_implementations)
def test_basic(unregistered_sorting_algorithm: str,
               sorting_implementation: Implementation) -> None:
    result = register_implementation(unregistered_sorting_algorithm,
                                     sorting_implementation)

    assert result is sorting_implementation
    assert is_algorithm_registered(unregistered_sorting_algorithm)


@given(strategies.unregistered_sorting_algorithms,
       strategies.sorting_implementations)
def test_currying(unregistered_sorting_algorithm: str,
                  sorting_implementation: Implementation) -> None:
    decorator = register_implementation(unregistered_sorting_algorithm)

    assert callable(decorator)
    assert not is_algorithm_registered(unregistered_sorting_algorithm)
    assert decorator(sorting_implementation) is sorting_implementation
    assert is_algorithm_registered(unregistered_sorting_algorithm)


def is_algorithm_registered(algorithm: str) -> bool:
    return algorithm in implementations
