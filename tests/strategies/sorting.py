from hypothesis import strategies

from lz.functional import identity
from lz.sorting import implementations
from .literals.factories import to_strings

sorting_keys = strategies.just(identity) | strategies.none()
registered_sorting_algorithms = strategies.sampled_from(list(implementations))


def is_algorithm_unregistered(algorithm: str) -> bool:
    return algorithm not in implementations


unregistered_sorting_algorithms = (to_strings(min_size=1)
                                   .filter(is_algorithm_unregistered))
