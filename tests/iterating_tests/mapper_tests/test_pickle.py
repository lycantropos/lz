from typing import Iterable

from hypothesis import given

from lz.hints import (Domain,
                      Map)
from lz.iterating import mapper
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.maps, strategies.maps_arguments_iterables)
def test_round_trip(map_: Map, arguments: Iterable[Domain]) -> None:
    original, target = duplicate(arguments)
    map_iterable = mapper(map_)

    result = round_trip_pickle(map_iterable)

    assert are_iterables_similar(result(target), map_iterable(original))
