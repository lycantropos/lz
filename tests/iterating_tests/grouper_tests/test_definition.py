from typing import (Any,
                    Hashable,
                    Iterable)

from hypothesis import given

from lz.hints import Map
from lz.iterating import grouper
from lz.replication import duplicate
from . import strategies


@given(strategies.hashables_iterables, strategies.keys_functions)
def test_basic(iterable: Iterable[Hashable],
               key_function: Map[Any, Hashable]) -> None:
    original, target = duplicate(iterable)
    group_by = grouper(key_function)

    result = group_by(target)
    result_dict = dict(result)

    assert all(element in result_dict[key_function(element)]
               for element in original)
