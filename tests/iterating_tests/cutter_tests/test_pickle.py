from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.iterating import cutter
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.iterables, strategies.non_negative_slices)
def test_round_trip(iterable: Iterable[Any], slice_: slice) -> None:
    original, target = duplicate(iterable)
    cut = cutter(slice_)

    result = round_trip_pickle(cut)

    assert are_iterables_similar(result(target), cut(original))
