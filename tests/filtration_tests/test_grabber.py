from typing import (Callable,
                    Iterable)

import pytest
from hypothesis import given

from lz.filtration import grabber
from lz.replication import duplicate
from tests import strategies
from tests.hints import Domain
from tests.utils import (are_iterables_similar,
                         are_objects_similar,
                         is_empty)


@given(strategies.iterables)
def test_basic(iterable: Iterable[Domain]) -> None:
    original, target = duplicate(iterable)
    grab = grabber(bool)

    result = grab(target)
    result_iterator = iter(result)

    for result_element, original_element in zip(result_iterator, original):
        if not original_element:
            break
        assert are_objects_similar(result_element, original_element)

    with pytest.raises(StopIteration):
        next(result_iterator)


@given(strategies.iterables, strategies.false_predicates)
def test_false_predicate(iterable: Iterable[Domain],
                         false_predicate: Callable[[Domain], bool]) -> None:
    skip_all = grabber(false_predicate)

    result = skip_all(iterable)

    assert is_empty(result)


@given(strategies.iterables, strategies.true_predicates)
def test_true_predicate(iterable: Iterable[Domain],
                        true_predicate: Callable[[Domain], bool]) -> None:
    original, target = duplicate(iterable)
    grab_all = grabber(true_predicate)

    result = grab_all(target)

    assert are_iterables_similar(result, original)
