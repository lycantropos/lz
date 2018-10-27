from itertools import tee
from typing import (Any,
                    Iterable)

from lz.iterating import (last,
                          slider,
                          trailer)
from tests.utils import (are_iterables_similar,
                         capacity)


def test_capacity(non_empty_iterable: Iterable[Any],
                  natural_number: int) -> None:
    original, target = tee(non_empty_iterable)
    trail = trailer(natural_number)

    result = trail(target)

    if capacity(original) < natural_number:
        assert capacity(result) < natural_number
    else:
        assert capacity(result) == natural_number


def test_elements(non_empty_iterable: Iterable[Any],
                  natural_number: int) -> None:
    original, target = tee(non_empty_iterable)
    trail = trailer(natural_number)
    slide = slider(natural_number)

    result = trail(target)
    slides = slide(original)

    assert are_iterables_similar(result, last(slides))
