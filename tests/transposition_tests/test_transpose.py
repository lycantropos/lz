from typing import (Any,
                    Collection,
                    Iterable)

import pytest
from hypothesis import given

from lz import (left,
                right)
from lz.replication import duplicate
from lz.transposition import transpose
from tests.utils import (are_iterables_similar,
                         is_empty,
                         iterable_ends_with,
                         iterable_starts_with)
from . import strategies


@given(strategies.empty_iterables)
def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = transpose(empty_iterable)

    assert is_empty(result)


@given(strategies.transposable_iterables,
       strategies.transposable_iterables_elements)
def test_step_left(transposable_iterable: Iterable[Collection[Any]],
                   transposable_iterable_element: Collection[Any]) -> None:
    original_element, target_element = duplicate(transposable_iterable_element)

    result = transpose(left.attacher(target_element)(transposable_iterable))

    assert all(iterable_starts_with(iterable, [coordinate])
               for iterable, coordinate in zip(result, original_element))


@given(strategies.transposable_iterables,
       strategies.transposable_iterables_elements)
def test_step_right(transposable_iterable: Iterable[Collection[Any]],
                    transposable_iterable_element: Collection[Any]
                    ) -> None:
    original_element, target_element = duplicate(transposable_iterable_element)

    result = transpose(right.attacher(target_element)(transposable_iterable))

    assert all(iterable_ends_with(iterable, [coordinate])
               for iterable, coordinate in zip(result, original_element))


@given(strategies.non_empty_transposable_iterables)
def test_involution(
        non_empty_transposable_iterable: Iterable[Collection[Any]]
) -> None:
    original, target = duplicate(non_empty_transposable_iterable)

    result = transpose(transpose(target))

    assert are_iterables_similar(result, original)


@given(strategies.scalars)
def test_unsupported_type(object_: Any) -> None:
    with pytest.raises(TypeError):
        transpose(object_)
