from itertools import tee
from typing import (Any,
                    Iterable)

from lz import (left,
                right)
from lz.iterating import (first,
                          last,
                          reverse)
from tests.utils import (are_iterables_similar,
                         is_empty)


def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = reverse(empty_iterable)

    assert is_empty(result)


def test_step_right(iterable: Iterable[Any],
                    object_: Any) -> None:
    attach = right.attacher(object_)

    result = reverse(attach(iterable))

    assert first(result) is object_


def test_step_left(iterable: Iterable[Any],
                   object_: Any) -> None:
    attach = left.attacher(object_)

    result = reverse(attach(iterable))

    assert last(result) is object_


def test_involution(iterable: Iterable[Any]) -> None:
    original, target = tee(iterable)

    result = reverse(reverse(target))

    assert are_iterables_similar(result, original)
