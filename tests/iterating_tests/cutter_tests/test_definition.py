from itertools import islice
from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.iterating import (capacity,
                          cutter)
from lz.replication import duplicate
from tests.configs import MAX_ITERABLES_SIZE
from tests.utils import are_iterables_similar
from . import strategies


@given(strategies.iterables, strategies.non_negative_slices)
def test_capacity(iterable: Iterable[Any], slice_: slice) -> None:
    cut = cutter(slice_)
    result = cut(iterable)

    assert capacity(result) <= slice_to_size(slice_)


@given(strategies.iterables, strategies.non_negative_slices)
def test_elements(iterable: Iterable[Any], slice_: slice) -> None:
    original, target = duplicate(iterable)

    cut = cutter(slice_)
    result = cut(target)

    assert are_iterables_similar(result,
                                 islice(original,
                                        slice_.start,
                                        slice_.stop,
                                        slice_.step))


def slice_to_size(slice_: slice) -> int:
    start, stop, step = slice_.indices(MAX_ITERABLES_SIZE)
    return max(1 + (stop - 1 - start) // step, 0)
