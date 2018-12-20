from typing import (Any,
                    Iterable)

from lz.iterating import trailer
from lz.replication import duplicate
from tests.utils import (capacity,
                         iterable_ends_with)


def test_capacity(non_empty_iterable: Iterable[Any],
                  size: int) -> None:
    original, target = duplicate(non_empty_iterable)
    trail = trailer(size)

    result = trail(target)

    if capacity(original) < size:
        assert capacity(result) < size
    else:
        assert capacity(result) == size


def test_elements(non_empty_iterable: Iterable[Any],
                  size: int) -> None:
    original, target = duplicate(non_empty_iterable)
    trail = trailer(size)

    result = trail(target)

    assert iterable_ends_with(original, result)
