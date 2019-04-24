from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.iterating import trailer
from lz.replication import duplicate
from tests import strategies
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


@given(strategies.non_empty_iterables, strategies.non_negative_indices)
def test_round_trip(non_empty_iterable: Iterable[Any], size: int) -> None:
    original, target = duplicate(non_empty_iterable)
    trail = trailer(size)

    result = round_trip_pickle(trail)

    assert are_iterables_similar(result(target), trail(original))
