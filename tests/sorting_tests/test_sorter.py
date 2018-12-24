from typing import Iterable

from lz.hints import Sortable
from lz.iterating import slider
from lz.replication import duplicate
from lz.sorting import (Key,
                        sorter)
from tests.utils import (are_iterables_similar,
                         capacity,
                         iterables_has_same_elements)


def test_order(sortable_iterable: Iterable[Sortable],
               registered_sorting_algorithm: str,
               sorting_key: Key) -> None:
    sort = sorter(algorithm=registered_sorting_algorithm,
                  key=sorting_key)

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


def objects_are_partially_ordered(left_object: Sortable,
                                  right_object: Sortable) -> bool:
    return left_object < right_object or not (right_object < left_object)


def test_capacity(sortable_iterable: Iterable[Sortable],
                  registered_sorting_algorithm: str,
                  sorting_key: Key) -> None:
    original, target = duplicate(sortable_iterable)
    sort = sorter(algorithm=registered_sorting_algorithm,
                  key=sorting_key)

    result = sort(target)

    assert capacity(result) == capacity(original)


def test_elements(sortable_iterable: Iterable[Sortable],
                  registered_sorting_algorithm: str,
                  sorting_key: Key) -> None:
    original, target = duplicate(sortable_iterable)
    sort = sorter(algorithm=registered_sorting_algorithm,
                  key=sorting_key)

    result = sort(target)

    assert iterables_has_same_elements(result, original)


def test_stability(sortable_iterable: Iterable[Sortable],
                   registered_stable_sorting_algorithm: str,
                   sorting_key: Key) -> None:
    first_target, second_target = duplicate(sortable_iterable)
    sort = sorter(algorithm=registered_stable_sorting_algorithm,
                  key=sorting_key)

    sorted_result = sort(first_target)
    double_sorted_result = sort(sort(second_target))

    assert are_iterables_similar(double_sorted_result, sorted_result)
