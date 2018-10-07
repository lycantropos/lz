from itertools import tee
from typing import Iterable

from lz.hints import Domain
from lz.iterating import (slider,
                          sorter)
from tests.utils import capacity


def test_order(sortable_iterable: Iterable[Domain]) -> None:
    sort = sorter()

    result = sort(sortable_iterable)

    elements_pairs = iter(slider(2)(result))
    try:
        element, next_element = next(elements_pairs)
    except ValueError:
        # iterable with no elements
        # or with single element are considered ordered
        return
    else:
        assert objects_are_partially_ordered(element, next_element)
    assert all(objects_are_partially_ordered(element, next_element)
               for element, next_element in elements_pairs)


def objects_are_partially_ordered(left_object: Domain,
                                  right_object: Domain) -> bool:
    return left_object < right_object or not (right_object < left_object)


def test_capacity(sortable_iterable: Iterable[Domain]) -> None:
    original, target = tee(sortable_iterable)
    sort = sorter()

    result = sort(target)

    assert capacity(result) == capacity(original)
