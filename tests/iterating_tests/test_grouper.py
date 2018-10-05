from itertools import tee
from typing import (Hashable,
                    Iterable)

from lz.hints import Map
from lz.iterating import grouper


def test_basic(hashables_iterable: Iterable[Hashable],
               grouper_key: Map[Hashable, Hashable]) -> None:
    original, target = tee(hashables_iterable)

    groups = grouper(grouper_key)(original)
    original_list = list(original)

    assert all(element in group
               for key, group in groups
               for element in original_list
               if grouper_key(element) == key)
