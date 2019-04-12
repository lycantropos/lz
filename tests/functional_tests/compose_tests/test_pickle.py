from typing import Sequence

from lz.functional import compose
from lz.hints import (Domain,
                      Map)
from tests.utils import round_trip_pickle


def test_round_trip(various_suitable_maps: Sequence[Map],
                    map_argument: Domain) -> None:
    composition = compose(*various_suitable_maps)

    result = round_trip_pickle(composition)

    assert result(map_argument) == composition(map_argument)
