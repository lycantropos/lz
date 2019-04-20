from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.iterating import (chopper,
                          flatten)
from lz.replication import duplicate
from tests import strategies
from tests.utils import are_iterables_similar


@given(strategies.iterables, strategies.non_negative_indices)
def test_size(iterable: Iterable[Any], size: int) -> None:
    chop = chopper(size)

    result = chop(iterable)

    assert all(len(element) <= size
               for element in result)


@given(strategies.iterables, strategies.non_negative_indices)
def test_elements(iterable: Iterable[Any], size: int) -> None:
    original, target = duplicate(iterable)
    chop = chopper(size)

    result = chop(target)

    assert not size or are_iterables_similar(flatten(result), original)
