from itertools import tee
from typing import (Any,
                    Hashable,
                    Iterable)

from lz.hints import Map
from lz.iterating import grouper


def test_basic(hashable_iterable: Iterable[Any],
               grouper_key: Map[Any, Hashable]) -> None:
    original, target = tee(hashable_iterable)

    result = grouper(grouper_key)(target)
    result_list = list(result)

    assert all(element in group
               for element in original
               for key, group in result_list
               if grouper_key(element) == key)
