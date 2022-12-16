from hypothesis import given

from lz.functional import compose
from tests.hints import CompositionCall
from . import strategies


@given(strategies.two_maps_calls)
def test_base_case(maps_chain_call: CompositionCall) -> None:
    (next_suitable_map, suitable_map), map_argument = maps_chain_call
    composition = compose(next_suitable_map, suitable_map)

    assert (composition(map_argument)
            == next_suitable_map(suitable_map(map_argument)))


@given(strategies.three_or_more_maps_calls)
def test_step(maps_chain_call: CompositionCall) -> None:
    (next_suitable_map, *suitable_maps), map_argument = maps_chain_call
    composition = compose(*suitable_maps)
    next_composition = compose(next_suitable_map, *suitable_maps)

    result = composition(map_argument)
    next_result = next_composition(map_argument)

    assert next_result == next_suitable_map(result)
