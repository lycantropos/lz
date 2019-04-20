from typing import Sequence

from hypothesis import strategies

from lz.hints import Map
from tests.hints import (CombinationCall,
                         Strategy)
from tests.strategies import (maps,
                              maps_arguments,
                              positionals_arguments,
                              to_homogeneous_sequences)

positionals_arguments = positionals_arguments


def to_combination_calls(maps_sequence: Sequence[Map]
                         ) -> Strategy[CombinationCall]:
    return strategies.tuples(strategies.just(maps_sequence),
                             to_homogeneous_sequences(
                                     maps_arguments,
                                     min_size=len(maps_sequence),
                                     max_size=len(maps_sequence)))


combinations_calls = to_homogeneous_sequences(maps).flatmap(to_combination_calls)
non_empty_combination_calls = (to_homogeneous_sequences(maps,
                                                        min_size=1)
                               .flatmap(to_combination_calls))
