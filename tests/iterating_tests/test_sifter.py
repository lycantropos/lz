from typing import (Any,
                    Iterable)

from lz.hints import Predicate
from lz.iterating import sifter


def test_default_predicate(iterable: Iterable[Any]) -> None:
    sift = sifter()

    result = sift(iterable)

    assert all(result)


def test_custom_predicate(iterable: Iterable[Any],
                          predicate: Predicate) -> None:
    sift = sifter(predicate)

    result = sift(iterable)

    assert all(map(predicate, result))
