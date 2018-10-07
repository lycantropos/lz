from itertools import tee
from typing import (Any,
                    Iterable)

from lz.iterating import first


def test_basic(non_empty_iterable: Iterable[Any]) -> None:
    original, target = tee(non_empty_iterable)

    result = first(target)

    assert result is next(original)
