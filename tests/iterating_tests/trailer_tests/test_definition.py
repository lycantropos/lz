from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.iterating import (capacity,
                          trailer)
from lz.replication import duplicate
from tests import strategies
from tests.utils import iterable_ends_with


@given(strategies.non_empty_iterables, strategies.non_negative_indices)
def test_capacity(non_empty_iterable: Iterable[Any],
                  size: int) -> None:
    original, target = duplicate(non_empty_iterable)
    trail = trailer(size)

    result = trail(target)

    if capacity(original) < size:
        assert capacity(result) < size
    else:
        assert capacity(result) == size


@given(strategies.non_empty_iterables, strategies.non_negative_indices)
def test_elements(non_empty_iterable: Iterable[Any],
                  size: int) -> None:
    original, target = duplicate(non_empty_iterable)
    trail = trailer(size)

    result = trail(target)

    assert iterable_ends_with(original, result)
