from operator import not_
from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.filtration import scavenger
from lz.hints import Predicate
from lz.logical import negate
from tests import strategies


@given(strategies.iterables)
def test_default_predicate(iterable: Iterable[Any]) -> None:
    scavenge = scavenger()

    result = scavenge(iterable)

    assert all(map(not_, result))


@given(strategies.iterables, strategies.predicates)
def test_custom_predicate(iterable: Iterable[Any],
                          predicate: Predicate) -> None:
    scavenge = scavenger(predicate)

    result = scavenge(iterable)

    assert all(map(negate(predicate), result))
