from itertools import tee
from typing import (Any,
                    Iterable)

from lz.iterating import (chopper,
                          flatten)
from tests.utils import are_iterables_similar


def test_size(iterable: Iterable[Any],
              chopper_size: int) -> None:
    chop = chopper(chopper_size)

    result = chop(iterable)

    assert all(len(element) <= chopper_size
               for element in result)


def test_elements(iterable: Iterable[Any],
                  chopper_size: int) -> None:
    original, target = tee(iterable)
    chop = chopper(chopper_size)

    result = chop(target)

    assert are_iterables_similar(flatten(result), original)
