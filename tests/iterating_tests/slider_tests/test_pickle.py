from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.iterating import slider
from lz.replication import duplicate
from tests import strategies
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


@given(strategies.iterables, strategies.non_negative_indices)
def test_round_trip(iterable: Iterable[Any], size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(size)

    result = round_trip_pickle(slide)

    assert are_iterables_similar(result(target), slide(original))
