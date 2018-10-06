from itertools import (islice,
                       tee)
from numbers import Real
from typing import (Any,
                    Iterable)

from lz.iterating import cutter
from tests.utils import (are_iterables_similar,
                         capacity)


def test_size(iterable: Iterable[Any],
              cutter_slice: slice) -> None:
    cut = cutter(cutter_slice)
    result = cut(iterable)

    assert capacity(result) <= slice_to_size(cutter_slice)


def test_elements(iterable: Iterable[Any],
                  cutter_slice: slice) -> None:
    original, target = tee(iterable)

    cut = cutter(cutter_slice)
    result = cut(target)

    assert are_iterables_similar(result,
                                 islice(original,
                                        cutter_slice.start,
                                        cutter_slice.stop,
                                        cutter_slice.step))


def slice_to_size(slice_: slice) -> Real:
    stop = slice_.stop
    if stop is None:
        return float('inf')
    start = slice_.start or 0
    step = slice_.step or 1
    return (stop - start) / step
