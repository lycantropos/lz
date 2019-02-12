from typing import (Any,
                    Iterable)

from lz import (left,
                right)
from lz.iterating import capacity
from lz.replication import duplicate


def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = capacity(empty_iterable)

    assert result == 0


def test_step_right(iterable: Iterable[Any],
                    object_: Any) -> None:
    original, target = duplicate(iterable)
    attach = right.attacher(object_)

    result = capacity(attach(target))

    assert result == capacity(original) + 1


def test_step_left(iterable: Iterable[Any],
                   object_: Any) -> None:
    original, target = duplicate(iterable)
    attach = left.attacher(object_)

    result = capacity(attach(target))

    assert result == capacity(original) + 1
