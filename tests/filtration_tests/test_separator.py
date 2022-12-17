from operator import not_
from typing import (Any,
                    Callable,
                    Iterable)

from hypothesis import given

from lz.filtration import separator
from lz.logical import negate
from tests import strategies
from tests.hints import Domain


@given(strategies.iterables)
def test_default_predicate(iterable: Iterable[Any]) -> None:
    separate = separator(bool)

    false_like, true_like = separate(iterable)

    assert all(map(not_, false_like))
    assert all(true_like)


@given(strategies.iterables, strategies.predicates)
def test_custom_predicate(iterable: Iterable[Domain],
                          predicate: Callable[[Domain], bool]) -> None:
    separate = separator(predicate)

    dissatisfied, satisfied = separate(iterable)

    assert all(map(negate(predicate), dissatisfied))
    assert all(map(predicate, satisfied))
