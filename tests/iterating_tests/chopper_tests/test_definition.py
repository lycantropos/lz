from typing import (Any,
                    Iterable)

from lz.iterating import (chopper,
                          flatten)
from lz.replication import duplicate
from tests.utils import are_iterables_similar


def test_size(iterable: Iterable[Any],
              size: int) -> None:
    chop = chopper(size)

    result = chop(iterable)

    assert all(len(element) <= size
               for element in result)


def test_elements(iterable: Iterable[Any],
                  size: int) -> None:
    original, target = duplicate(iterable)
    chop = chopper(size)

    result = chop(target)

    assert are_iterables_similar(flatten(result), original)
