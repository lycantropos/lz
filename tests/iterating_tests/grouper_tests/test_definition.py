from typing import (Any,
                    Hashable,
                    Iterable)

from hypothesis import given

from lz.hints import Map
from lz.iterating import grouper
from lz.replication import duplicate
from . import strategies


@given(strategies.hashables_iterables, strategies.groupers_keys)
def test_basic(iterable: Iterable[Hashable], key: Map[Any, Hashable]) -> None:
    original, target = duplicate(iterable)
    group_by = grouper(key)

    result = group_by(target)
    result_list = list(result)

    assert all(element in group
               for element in original
               for key, group in result_list
               if key(element) == key)
