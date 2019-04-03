from typing import (Any,
                    Iterable)

from lz.iterating import chopper
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


def test_round_trip(iterable: Iterable[Any],
                    size: int) -> None:
    original, target = duplicate(iterable)
    chop = chopper(size)

    result = round_trip_pickle(chop)

    assert are_iterables_similar(result(target), chop(original))
