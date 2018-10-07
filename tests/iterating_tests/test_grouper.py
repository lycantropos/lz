from itertools import tee
from typing import (Any,
                    Hashable,
                    Iterable)

from lz.hints import Map
from lz.iterating import grouper


def test_basic(iterable: Iterable[Any],
               grouper_key: Map[Any, Hashable]) -> None:
    original, target = tee(iterable)

    groups = grouper(grouper_key)(target)
    original_list = list(original)

    assert all(element in group
               for key, group in groups
               for element in original_list
               if grouper_key(element) == key)
