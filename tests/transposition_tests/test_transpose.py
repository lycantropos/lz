from typing import (Any,
                    Iterable)

from lz import (left,
                right)
from lz.hints import FiniteIterable
from lz.replication import duplicate
from lz.transposition import transpose
from tests.utils import (is_empty,
                         iterable_ends_with,
                         iterable_starts_with)


def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = transpose(empty_iterable)

    assert is_empty(result)


def test_step_left(transposable_iterable: Iterable[FiniteIterable[Any]],
                   transposable_iterable_element: FiniteIterable[Any]) -> None:
    original_element, target_element = duplicate(transposable_iterable_element)

    result = transpose(left.attacher(target_element)(transposable_iterable))

    assert all(iterable_starts_with(iterable, [coordinate])
               for iterable, coordinate in zip(result, original_element))


def test_step_right(transposable_iterable: Iterable[FiniteIterable[Any]],
                    transposable_iterable_element: FiniteIterable[Any]
                    ) -> None:
    original_element, target_element = duplicate(transposable_iterable_element)

    result = transpose(right.attacher(target_element)(transposable_iterable))

    assert all(iterable_ends_with(iterable, [coordinate])
               for iterable, coordinate in zip(result, original_element))
