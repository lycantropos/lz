from itertools import islice
from typing import (Any,
                    Iterable)

from lz.iterating import cutter
from lz.replication import duplicate
from tests.configs import MAX_ITERABLES_SIZE
from tests.utils import (are_iterables_similar,
                         capacity)


def test_capacity(iterable: Iterable[Any],
                  cutter_slice: slice) -> None:
    cut = cutter(cutter_slice)
    result = cut(iterable)

    assert capacity(result) <= slice_to_size(cutter_slice)


def test_elements(iterable: Iterable[Any],
                  cutter_slice: slice) -> None:
    original, target = duplicate(iterable)

    cut = cutter(cutter_slice)
    result = cut(target)

    assert are_iterables_similar(result,
                                 islice(original,
                                        cutter_slice.start,
                                        cutter_slice.stop,
                                        cutter_slice.step))


def slice_to_size(slice_: slice) -> int:
    start, stop, step = slice_.indices(MAX_ITERABLES_SIZE)
    return max(1 + (stop - 1 - start) // step, 0)
