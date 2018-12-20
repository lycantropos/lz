from typing import (Any,
                    Iterable,
                    Tuple)

from lz import (left,
                right)
from lz.iterating import unzip
from lz.replication import duplicate
from tests.utils import (is_empty,
                         iterable_ends_with,
                         iterable_starts_with)


def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = unzip(empty_iterable)

    assert is_empty(result)


def test_step_left(zip_iterable: Iterable[Tuple[Any, ...]],
                   zip_iterable_element: Tuple[Any, ...]) -> None:
    original_element, target_element = duplicate(zip_iterable_element)

    result = unzip(left.attacher(target_element)(zip_iterable))

    assert all(iterable_starts_with(iterable, [coordinate])
               for iterable, coordinate in zip(result, original_element))


def test_step_right(zip_iterable: Iterable[Tuple[Any, ...]],
                    zip_iterable_element: Tuple[Any, ...]) -> None:
    original_element, target_element = duplicate(zip_iterable_element)

    result = unzip(right.attacher(target_element)(zip_iterable))

    assert all(iterable_ends_with(iterable, [coordinate])
               for iterable, coordinate in zip(result, original_element))
