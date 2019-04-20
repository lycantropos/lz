from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.iterating import chopper
from lz.replication import duplicate
from tests import strategies
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


@given(strategies.iterables, strategies.non_negative_indices)
def test_round_trip(iterable: Iterable[Any], size: int) -> None:
    original, target = duplicate(iterable)
    chop = chopper(size)

    result = round_trip_pickle(chop)

    assert are_iterables_similar(result(target), chop(original))
