from hypothesis import given

from lz.functional import (cleave,
                           compose,
                           curry,
                           flip)
from tests.hints import (CleavageCall,
                         CompositionCall,
                         FunctionCall)
from . import strategies


@given(strategies.transparent_functions_calls)
def test_involution(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    double_flipped = flip(flip(function))

    original_result = function(*args, **kwargs)
    double_flipped_result = double_flipped(*args, **kwargs)

    assert double_flipped_result == original_result


@given(strategies.cleavage_calls)
def test_cleavage(cleavage_call: CleavageCall) -> None:
    maps, argument = cleavage_call
    flipped_cleavage = flip(cleave(*maps))
    cleavage_of_flipped = cleave(*[flip(map_) for map_ in maps])

    assert flipped_cleavage(argument) == cleavage_of_flipped(argument)


@given(strategies.two_or_more_maps_calls)
def test_composition(maps_chain_call: CompositionCall) -> None:
    (*rest_maps, first_suitable_map), map_argument = maps_chain_call
    flipped_composition = flip(compose(*rest_maps, first_suitable_map))
    composition_with_flipped = compose(*rest_maps, flip(first_suitable_map))

    assert (flipped_composition(map_argument)
            == composition_with_flipped(map_argument))


@given(strategies.transparent_functions_calls)
def test_currying(function_call: FunctionCall) -> None:
    function, args, kwargs = function_call
    flipped = flip(function)
    curried_flipped = curry(flipped)

    result = curried_flipped(*args[::-1], **kwargs)

    assert result == flipped(*args[::-1], **kwargs)
