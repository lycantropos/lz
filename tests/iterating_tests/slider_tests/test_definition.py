from itertools import islice
from typing import (Any,
                    Iterable)

from hypothesis import given

from lz import (left,
                right)
from lz.iterating import (capacity,
                          first,
                          flatten,
                          last,
                          slider)
from lz.replication import duplicate
from tests import strategies
from tests.utils import (are_iterables_similar,
                         is_empty)


@given(strategies.iterables)
def test_base_case_by_size_capacity(iterable: Iterable[Any]) -> None:
    target, original = duplicate(iterable)
    slide = slider(0)

    result = slide(target)

    assert capacity(result) == capacity(original) + 1


@given(strategies.iterables)
def test_base_case_by_size_elements(iterable: Iterable[Any]) -> None:
    target, original = duplicate(iterable)
    slide = slider(0)

    result = slide(target)
    result_iterator = iter(result)

    assert is_empty(first(result_iterator))
    assert are_iterables_similar(flatten(result_iterator),
                                 original)


@given(strategies.iterables, strategies.non_negative_indices)
def test_step_by_size_total_capacity(iterable: Iterable[Any],
                                     size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(size + 1)

    result = slide(target)

    assert 0 <= capacity(slider(size)(original)) - capacity(result) <= 1


@given(strategies.iterables, strategies.non_negative_indices)
def test_step_by_size_elementwise_capacity(iterable: Iterable[Any],
                                           size: int) -> None:
    slide = slider(size + 1)

    result = slide(iterable)

    assert all(0 <= capacity(element) <= size + 1
               for element in result)


@given(strategies.iterables, strategies.non_negative_indices)
def test_step_by_size_elements(iterable: Iterable[Any], size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(size + 1)

    result = slide(target)

    assert are_iterables_similar(first(result),
                                 islice(original, size + 1))


@given(strategies.empty.iterables, strategies.non_negative_indices)
def test_base_case_by_iterable_capacity(empty_iterable: Iterable[Any],
                                        size: int) -> None:
    slide = slider(size + 1)

    result = slide(empty_iterable)

    assert capacity(result) == 1


@given(strategies.empty.iterables, strategies.non_negative_indices)
def test_base_case_by_iterable_elements(empty_iterable: Iterable[Any],
                                        size: int) -> None:
    slide = slider(size + 1)

    result = slide(empty_iterable)

    assert all(map(is_empty, result))


@given(strategies.iterables,
       strategies.scalars,
       strategies.non_negative_indices)
def test_step_left_by_iterable_total_capacity(iterable: Iterable[Any],
                                              object_: Any,
                                              size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(size + 1)
    attach = left.attacher(object_)

    result = slide(attach(target))

    assert 0 <= capacity(result) - capacity(slide(original)) <= 1


@given(strategies.iterables,
       strategies.scalars,
       strategies.non_negative_indices)
def test_step_left_by_iterable_elementwise_capacity(iterable: Iterable[Any],
                                                    object_: Any,
                                                    size: int) -> None:
    slide = slider(size + 1)
    attach = left.attacher(object_)

    result = slide(attach(iterable))

    assert all(0 <= capacity(element) <= size + 1
               for element in result)


@given(strategies.iterables,
       strategies.scalars,
       strategies.non_negative_indices)
def test_step_left_by_iterable_elements(iterable: Iterable[Any],
                                        object_: Any,
                                        size: int) -> None:
    slide = slider(size + 1)
    attach = left.attacher(object_)

    result = slide(attach(iterable))

    assert first(first(result)) is object_


@given(strategies.iterables,
       strategies.scalars,
       strategies.non_negative_indices)
def test_step_right_by_iterable_total_capacity(iterable: Iterable[Any],
                                               object_: Any,
                                               size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(size + 1)
    attach = right.attacher(object_)

    result = slide(attach(target))

    assert 0 <= capacity(result) - capacity(slide(original)) <= 1


@given(strategies.iterables,
       strategies.scalars,
       strategies.non_negative_indices)
def test_step_right_by_iterable_elementwise_capacity(iterable: Iterable[Any],
                                                     object_: Any,
                                                     size: int) -> None:
    slide = slider(size + 1)
    attach = right.attacher(object_)

    result = slide(attach(iterable))

    assert all(0 <= capacity(element) <= size + 1
               for element in result)


@given(strategies.iterables,
       strategies.scalars,
       strategies.non_negative_indices)
def test_step_right_by_iterable_elements(iterable: Iterable[Any],
                                         object_: Any,
                                         size: int) -> None:
    slide = slider(size + 1)
    attach = right.attacher(object_)

    result = slide(attach(iterable))

    assert last(last(result)) is object_
