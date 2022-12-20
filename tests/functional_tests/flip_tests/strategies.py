from hypothesis import strategies

from tests.strategies import (maps,
                              maps_arguments,
                              to_homogeneous_sequences,
                              transparent_functions_calls,
                              two_or_more_suitable_maps)

two_or_more_maps_calls = strategies.tuples(two_or_more_suitable_maps,
                                           maps_arguments)
transparent_functions_calls = transparent_functions_calls
cleavage_calls = strategies.tuples(to_homogeneous_sequences(maps),
                                   maps_arguments)
