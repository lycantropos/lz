from itertools import tee
from typing import Iterable

import pytest

from lz.hints import (Domain,
                      Predicate)
from lz.iterating import kicker
from tests.utils import (are_iterables_similar,
                         capacity)


def test_basic(iterable: Iterable[Domain]) -> None:
    original, target = tee(iterable)
    kick = kicker()

    result = kick(target)
    result_iterator = iter(result)

    for original_element in original:
        if not original_element:
            assert original_element is next(result_iterator)
            break

    for result_element, original_element in zip(result_iterator, original):
        assert result_element is original_element

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_false_predicate(iterable: Iterable[Domain],
                         false_predicate: Predicate) -> None:
    original, target = tee(iterable)
    keep_all = kicker(false_predicate)

    keep_all_result = keep_all(target)

    assert are_iterables_similar(keep_all_result, original)


def test_true_predicate(iterable: Iterable[Domain],
                        true_predicate: Predicate) -> None:
    kick_all = kicker(true_predicate)

    kick_all_result = kick_all(iterable)

    assert capacity(kick_all_result) == 0
