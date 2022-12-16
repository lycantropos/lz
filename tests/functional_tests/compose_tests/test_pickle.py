from hypothesis import given

from lz.functional import compose
from tests.hints import CompositionCall
from tests.utils import round_trip_pickle
from . import strategies


@given(strategies.two_or_more_maps_calls)
def test_round_trip(maps_chain_call: CompositionCall) -> None:
    various_suitable_maps, map_argument = maps_chain_call
    composition = compose(*various_suitable_maps)

    result = round_trip_pickle(composition)

    assert result(map_argument) == composition(map_argument)
