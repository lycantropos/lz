from typing import Sequence

from lz.functional import cleave
from lz.hints import (Domain,
                      Map)
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


def test_round_trip(maps: Sequence[Map],
                    map_argument: Domain) -> None:
    cleavage = cleave(*maps)

    result = round_trip_pickle(cleavage)

    assert are_iterables_similar(result(map_argument), cleavage(map_argument))
