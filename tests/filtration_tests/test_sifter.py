from typing import (Any,
                    Callable,
                    Iterable)

from hypothesis import given

from lz.filtration import sifter
from tests import strategies
from tests.hints import Domain


@given(strategies.iterables)
def test_default_predicate(iterable: Iterable[Any]) -> None:
    sift = sifter(bool)

    result = sift(iterable)

    assert all(result)


@given(strategies.iterables, strategies.predicates)
def test_custom_predicate(iterable: Iterable[Domain],
                          predicate: Callable[[Domain], bool]) -> None:
    sift = sifter(predicate)

    result = sift(iterable)

    assert all(map(predicate, result))
