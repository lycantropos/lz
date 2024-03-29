from typing import (Any,
                    Callable,
                    Hashable,
                    Iterable)

from hypothesis import given

from lz.iterating import grouper
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.hashables_iterables, strategies.keys_functions)
def test_round_trip(iterable: Iterable[Hashable],
                    key_function: Callable[[Any], Hashable]) -> None:
    original, target = duplicate(iterable)
    group_by = grouper(key_function)

    result = round_trip_pickle(group_by)

    assert are_iterables_similar(result(target), group_by(original))
