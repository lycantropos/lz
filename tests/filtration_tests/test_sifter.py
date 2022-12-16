from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.filtration import sifter
from lz.hints import Predicate
from tests import strategies


@given(strategies.iterables)
def test_default_predicate(iterable: Iterable[Any]) -> None:
    sift = sifter(bool)

    result = sift(iterable)

    assert all(result)


@given(strategies.iterables, strategies.predicates)
def test_custom_predicate(iterable: Iterable[Any],
                          predicate: Predicate) -> None:
    sift = sifter(predicate)

    result = sift(iterable)

    assert all(map(predicate, result))
