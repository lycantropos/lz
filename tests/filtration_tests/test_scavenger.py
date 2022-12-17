from operator import not_
from typing import (Any,
                    Callable,
                    Iterable)

from hypothesis import given

from lz.filtration import scavenger
from lz.logical import negate
from tests import strategies
from tests.hints import Domain


@given(strategies.iterables)
def test_default_predicate(iterable: Iterable[Any]) -> None:
    scavenge = scavenger(bool)

    result = scavenge(iterable)

    assert all(map(not_, result))


@given(strategies.iterables, strategies.predicates)
def test_custom_predicate(iterable: Iterable[Domain],
                          predicate: Callable[[Domain], bool]) -> None:
    scavenge = scavenger(predicate)

    result = scavenge(iterable)

    assert all(map(negate(predicate), result))
