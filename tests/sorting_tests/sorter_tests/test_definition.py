from typing import Iterable

from hypothesis import given

from lz.hints import Sortable
from lz.iterating import (capacity,
                          slider)
from lz.replication import duplicate
from lz.sorting import (Key,
                        sorter)
from tests.utils import iterables_has_same_elements
from . import strategies


@given(strategies.sortable_iterables,
       strategies.registered_sorting_algorithms,
       strategies.sorting_keys)
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


@given(strategies.sortable_iterables,
       strategies.registered_sorting_algorithms,
       strategies.sorting_keys)
def test_capacity(sortable_iterable: Iterable[Sortable],
                  registered_sorting_algorithm: str,
                  sorting_key: Key) -> None:
    original, target = duplicate(sortable_iterable)
    sort = sorter(algorithm=registered_sorting_algorithm,
                  key=sorting_key)

    result = sort(target)

    assert capacity(result) == capacity(original)


@given(strategies.sortable_iterables,
       strategies.registered_sorting_algorithms,
       strategies.sorting_keys)
def test_elements(sortable_iterable: Iterable[Sortable],
                  registered_sorting_algorithm: str,
                  sorting_key: Key) -> None:
    original, target = duplicate(sortable_iterable)
    sort = sorter(algorithm=registered_sorting_algorithm,
                  key=sorting_key)

    result = sort(target)

    assert iterables_has_same_elements(result, original)
