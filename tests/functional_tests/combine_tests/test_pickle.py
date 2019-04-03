from typing import Sequence

from lz.functional import combine
from lz.hints import (Domain,
                      Map)
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


def test_round_trip(maps: Sequence[Map],
                    maps_arguments: Sequence[Domain]) -> None:
    combination = combine(*maps)

    result = round_trip_pickle(combination)

    assert are_iterables_similar(result(maps_arguments),
                                 combination(maps_arguments))
