from typing import (Any,
                    Hashable,
                    Iterable)

from lz.hints import Map
from lz.iterating import grouper
from lz.replication import duplicate


def test_basic(hashables_iterable: Iterable[Hashable],
               grouper_key: Map[Any, Hashable]) -> None:
    original, target = duplicate(hashables_iterable)
    group_by = grouper(grouper_key)

    result = group_by(target)
    result_list = list(result)

    assert all(element in group
               for element in original
               for key, group in result_list
               if grouper_key(element) == key)