from typing import (Callable,
                    Iterable)

import pytest
from hypothesis import given

from lz.filtration import kicker
from lz.replication import duplicate
from tests import strategies
from tests.hints import Domain
from tests.utils import (are_iterables_similar,
                         are_objects_similar,
                         is_empty)


@given(strategies.iterables)
def test_basic(iterable: Iterable[Domain]) -> None:
    original, target = duplicate(iterable)
    kick = kicker(bool)

    result = kick(target)
    result_iterator = iter(result)
    original_iterator = iter(original)

    for original_element in original_iterator:
        if not original_element:
            assert are_objects_similar(original_element, next(result_iterator))
            break

    for result_element, original_element in zip(result_iterator,
                                                original_iterator):
        assert are_objects_similar(result_element, original_element)

    with pytest.raises(StopIteration):
        next(result_iterator)


@given(strategies.iterables, strategies.false_predicates)
def test_false_predicate(iterable: Iterable[Domain],
                         false_predicate: Callable[[Domain], bool]) -> None:
    original, target = duplicate(iterable)
    keep_all = kicker(false_predicate)

    result = keep_all(target)

    assert are_iterables_similar(result, original)


@given(strategies.iterables, strategies.true_predicates)
def test_true_predicate(iterable: Iterable[Domain],
                        true_predicate: Callable[[Domain], bool]) -> None:
    kick_all = kicker(true_predicate)

    result = kick_all(iterable)

    assert is_empty(result)
