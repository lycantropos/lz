from hypothesis import strategies

from lz.functional import identity
from tests.sorting_tests.strategies import registered_sorting_algorithms
from tests.strategies import (sortable_domains,
                              to_homogeneous_iterables)

registered_sorting_algorithms = registered_sorting_algorithms
sortable_iterables = strategies.one_of(*map(to_homogeneous_iterables,
                                            sortable_domains))
sorting_keys = strategies.just(identity) | strategies.none()
