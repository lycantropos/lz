from typing import (Any,
                    Iterable)

from lz.iterating import header
from lz.replication import duplicate
from tests.utils import (capacity,
                         iterable_starts_with)


def test_capacity(non_empty_iterable: Iterable[Any],
                  size: int) -> None:
    original, target = duplicate(non_empty_iterable)
    head = header(size)

    result = head(target)

    if capacity(original) < size:
        assert capacity(result) < size
    else:
        assert capacity(result) == size


def test_elements(non_empty_iterable: Iterable[Any],
                  size: int) -> None:
    original, target = duplicate(non_empty_iterable)
    head = header(size)

    result = head(target)

    assert iterable_starts_with(original, result)
