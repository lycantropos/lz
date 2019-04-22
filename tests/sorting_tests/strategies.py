from hypothesis import strategies

from lz.sorting import implementations

sorting_implementations = strategies.sampled_from(list(implementations
                                                       .values()))
registered_sorting_algorithms = strategies.sampled_from(list(implementations))


def is_algorithm_unregistered(algorithm: str) -> bool:
    return algorithm not in implementations


unregistered_sorting_algorithms = (strategies.text(min_size=1)
                                   .filter(is_algorithm_unregistered))
