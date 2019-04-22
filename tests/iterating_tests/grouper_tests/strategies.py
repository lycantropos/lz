from functools import partial
from typing import Hashable

from hypothesis import strategies

from lz.functional import identity
from lz.hints import (Domain,
                      Map)
from tests.hints import Strategy
from tests.strategies import (scalars,
                              min_iterables_sizes,
                              to_homogeneous_iterables)


def grouper_key(object_: Hashable,
                odd_order: int = 1) -> Hashable:
    return hash(object_) ** odd_order


def to_key_function(odd_order: int) -> Map[Hashable, Hashable]:
    return partial(grouper_key,
                   odd_order=odd_order)


def is_odd(number: int) -> bool:
    return bool(number & 1)


keys_functions = (strategies.sampled_from(range(1, 1000, 2))
                  .map(to_key_function)
                  | strategies.just(identity))


def to_iterables(min_size: int,
                 *,
                 elements: Strategy[Domain]) -> Strategy:
    return to_homogeneous_iterables(elements,
                                    min_size=min_size)


hashables_iterables = min_iterables_sizes.flatmap(partial(to_iterables,
                                                          elements=scalars))
plain_hashables_iterables = (min_iterables_sizes
                             .flatmap(partial(to_iterables,
                                              elements=scalars)))
