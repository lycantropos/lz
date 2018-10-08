from itertools import tee
from typing import Iterable

from lz.hints import Domain
from lz.iterating import (slider,
                          sorter)
from tests.utils import (are_iterables_similar,
                         capacity)


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


def test_elements(sortable_iterable: Iterable[Domain]) -> None:
    original, target = tee(sortable_iterable)
    sort = sorter()

    result = sort(target)
    original_list = list(original)

    assert all(element in original_list
               for element in result)


def test_idempotence(sortable_iterable: Iterable[Domain]) -> None:
    first_target, second_target = tee(sortable_iterable)
    sort = sorter()

    sorted_result = sort(first_target)
    double_sorted_result = sort(sort(second_target))

    assert are_iterables_similar(double_sorted_result, sorted_result)
