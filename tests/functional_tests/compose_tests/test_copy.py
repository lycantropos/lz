import copy

from hypothesis import given

from lz.functional import compose
from tests.hints import MapsChainCall
from . import strategies


@given(strategies.maps_chain_calls)
def test_shallow(maps_chain_call: MapsChainCall) -> None:
    various_suitable_maps, map_argument = maps_chain_call
    composition = compose(*various_suitable_maps)

    shallow_copy = copy.copy(composition)

    assert shallow_copy is not composition
    assert shallow_copy(map_argument) == composition(map_argument)


@given(strategies.maps_chain_calls)
def test_deep(maps_chain_call: MapsChainCall) -> None:
    various_suitable_maps, map_argument = maps_chain_call
    composition = compose(*various_suitable_maps)

    deep_copy = copy.deepcopy(composition)

    assert deep_copy is not composition
    assert deep_copy(map_argument) == composition(map_argument)
