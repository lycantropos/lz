from typing import (Any,
                    Iterable)

from lz.iterating import cutter
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


def test_round_trip(iterable: Iterable[Any],
                    cutter_slice: slice) -> None:
    original, target = duplicate(iterable)
    cut = cutter(cutter_slice)

    result = round_trip_pickle(cut)

    assert are_iterables_similar(result(target), cut(original))
