from typing import Iterable

import pytest

from lz.hints import (Domain,
                      Predicate)
from lz.iterating import (duplicate,
                          grabber)
from tests.utils import (are_iterables_similar,
                         capacity)


def test_basic(iterable: Iterable[Domain]) -> None:
    original, target = duplicate(iterable)
    grab = grabber()

    result = grab(target)
    result_iterator = iter(result)

    for result_element, original_element in zip(result_iterator, original):
        if not original_element:
            break
        assert result_element is original_element

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_false_predicate(iterable: Iterable[Domain],
                         false_predicate: Predicate) -> None:
    skip_all = grabber(false_predicate)

    skip_all_result = skip_all(iterable)

    assert capacity(skip_all_result) == 0


def test_true_predicate(iterable: Iterable[Domain],
                        true_predicate: Predicate) -> None:
    original, target = duplicate(iterable)
    grab_all = grabber(true_predicate)

    grab_all_result = grab_all(target)

    assert are_iterables_similar(grab_all_result, original)
