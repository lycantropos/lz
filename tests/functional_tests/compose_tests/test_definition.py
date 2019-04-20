from typing import (Any,
                    Callable)

from hypothesis import given

from lz.functional import compose
from tests.hints import MapsChainCall
from . import strategies


@given(strategies.callables)
def test_base_case(callable_: Callable[..., Any]) -> None:
    composition = compose(callable_)

    assert composition is callable_


@given(strategies.maps_chain_calls)
def test_step(maps_chain_call: MapsChainCall) -> None:
    (next_suitable_map, *suitable_maps), map_argument = maps_chain_call
    composition = compose(*suitable_maps)
    next_composition = compose(next_suitable_map, *suitable_maps)

    result = composition(map_argument)
    next_result = next_composition(map_argument)

    assert next_result == next_suitable_map(result)
