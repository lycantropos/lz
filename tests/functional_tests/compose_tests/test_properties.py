from typing import Callable, Tuple

from hypothesis import given

from lz.functional import (compose,
                           curry,
                           identity)
from lz.hints import (Domain,
                      Range)
from tests.hints import CompositionCall
from . import strategies


@given(strategies.maps_calls)
def test_identity(map_call: Tuple[Callable[[Domain], Range], Domain]) -> None:
    map_, map_argument = map_call
    left_composition = compose(identity, map_)
    right_composition = compose(map_, identity)

    left_composition_result = left_composition(map_argument)
    right_composition_result = right_composition(map_argument)

    assert left_composition_result == right_composition_result


@given(strategies.maps_triplets_calls)
def test_associativity(maps_triplet_call: CompositionCall) -> None:
    (last_map, next_map, map_), map_argument = maps_triplet_call
    left_composition = compose(compose(last_map, next_map), map_)
    right_composition = compose(last_map, compose(next_map, map_))

    left_composition_result = left_composition(map_argument)
    right_composition_result = right_composition(map_argument)

    assert left_composition_result == right_composition_result


@given(strategies.two_maps_calls)
def test_currying(maps_chain_call: CompositionCall) -> None:
    (next_suitable_map, *suitable_maps), map_argument = maps_chain_call
    composition = compose(next_suitable_map, *suitable_maps)
    curried_composition = curry(composition)

    result = curried_composition(map_argument)

    assert result == composition(map_argument)
