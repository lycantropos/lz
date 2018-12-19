from typing import (Any,
                    Iterable)

from lz import (left,
                right)
from lz.iterating import flatten
from lz.replication import duplicate
from tests.utils import (is_empty,
                         iterable_ends_with,
                         iterable_starts_with)


def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = flatten(empty_iterable)

    assert is_empty(result)


def test_step_left(nested_iterable: Iterable[Iterable[Any]],
                   iterable: Iterable[Any]) -> None:
    original, target = duplicate(iterable)
    attach = left.attacher(target)

    result = flatten(attach(nested_iterable))

    assert iterable_starts_with(result, original)


def test_step_right(nested_iterable: Iterable[Iterable[Any]],
                    iterable: Iterable[Any]) -> None:
    original, target = duplicate(iterable)
    attach = right.attacher(target)

    result = flatten(attach(nested_iterable))

    assert iterable_ends_with(result, original)
