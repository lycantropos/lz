from operator import not_
from typing import (Any,
                    Iterable)

from lz.hints import Predicate
from lz.iterating import scavenger
from lz.logical import negate


def test_default_predicate(iterable: Iterable[Any]) -> None:
    scavenge = scavenger()

    result = scavenge(iterable)

    assert all(map(not_, result))


def test_custom_predicate(iterable: Iterable[Any],
                          predicate: Predicate) -> None:
    scavenge = scavenger(predicate)

    result = scavenge(iterable)

    assert all(map(negate(predicate), result))
