from itertools import tee
from typing import (Any,
                    Iterable)

from lz.iterating import cutter
from tests.utils import has_same_elements


def test_basic(iterable: Iterable[Any],
               cutter_slice: slice) -> None:
    original, target = tee(iterable)

    cut = cutter(cutter_slice)
    result = cut(target)
    original_list = list(original)

    assert has_same_elements(result, original_list[cutter_slice])
