from typing import Iterable

import pytest

from lz.filtration import grabber
from lz.hints import (Domain,
                      Predicate)
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         are_objects_similar,
                         is_empty)


def test_basic(iterable: Iterable[Domain]) -> None:
    original, target = duplicate(iterable)
    grab = grabber()

    result = grab(target)
    result_iterator = iter(result)

    for result_element, original_element in zip(result_iterator, original):
        if not original_element:
            break
        assert are_objects_similar(result_element, original_element)

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_false_predicate(iterable: Iterable[Domain],
                         false_predicate: Predicate) -> None:
    skip_all = grabber(false_predicate)

    result = skip_all(iterable)

    assert is_empty(result)


def test_true_predicate(iterable: Iterable[Domain],
                        true_predicate: Predicate) -> None:
    original, target = duplicate(iterable)
    grab_all = grabber(true_predicate)

    result = grab_all(target)

    assert are_iterables_similar(result, original)
