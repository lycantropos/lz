from hypothesis import strategies

from tests.strategies import (callables,
                              maps,
                              maps_arguments,
                              various_suitable_maps)
from tests.strategies.functional import extend_suitable_maps

callables = callables
maps_calls = strategies.tuples(maps, maps_arguments)
maps_chain_calls = strategies.tuples(various_suitable_maps, maps_arguments)
maps_triplets_calls = strategies.tuples(
        extend_suitable_maps(extend_suitable_maps(strategies.tuples(maps))),
        maps_arguments)
