from hypothesis import strategies

from tests.strategies import (keywords_arguments,
                              maps,
                              maps_arguments,
                              positionals_arguments,
                              to_homogeneous_sequences)

keywords_arguments = keywords_arguments
positionals_arguments = positionals_arguments
cleavage_calls = strategies.tuples(to_homogeneous_sequences(maps,
                                                            min_size=1),
                                   maps_arguments)
non_empty_cleavage_calls = strategies.tuples(
        to_homogeneous_sequences(maps,
                                 min_size=1),
        maps_arguments)
