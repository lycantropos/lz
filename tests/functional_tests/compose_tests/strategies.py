from hypothesis import strategies

from tests.strategies import (callables,
                              empty,
                              maps,
                              maps_arguments,
                              three_or_more_suitable_maps,
                              two_or_more_suitable_maps,
                              two_suitable_maps)
from tests.strategies.functional import extend_suitable_maps
from tests.strategies.utils import identifiers

callables = callables
empty = empty
identifiers = identifiers
maps_calls = strategies.tuples(maps, maps_arguments)
two_maps_calls = strategies.tuples(two_suitable_maps, maps_arguments)
two_or_more_maps_calls = strategies.tuples(two_or_more_suitable_maps,
                                           maps_arguments)
three_or_more_maps_calls = strategies.tuples(three_or_more_suitable_maps,
                                             maps_arguments)
maps_triplets_calls = strategies.tuples(
        extend_suitable_maps(extend_suitable_maps(strategies.tuples(maps))),
        maps_arguments
)
