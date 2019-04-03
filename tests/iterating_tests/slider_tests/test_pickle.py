from typing import (Any,
                    Iterable)

from lz.iterating import slider
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


def test_round_trip(iterable: Iterable[Any],
                    size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(size)

    result = round_trip_pickle(slide)

    assert are_iterables_similar(result(target), slide(original))
