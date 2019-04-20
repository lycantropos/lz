from functools import partial
from typing import Hashable

from hypothesis import strategies

from lz.functional import identity
from lz.hints import Domain, Map
from tests.hints import Strategy
from tests.strategies import (hashables,
                              min_iterables_sizes,
                              plain_hashables,
                              to_homogeneous_iterables)


def grouper_key(object_: Hashable,
                odd_order: int = 1) -> Hashable:
    return hash(object_) ** odd_order


def to_grouper_key(odd_order: int) -> Map[Hashable, Hashable]:
    return partial(grouper_key,
                   odd_order=odd_order)


def is_odd(number: int) -> bool:
    return bool(number & 1)


groupers_keys = (strategies.integers(1, 1000)
                 .filter(is_odd)
                 .map(to_grouper_key)
                 | strategies.just(identity))


def to_iterables(min_size: int,
                 *,
                 elements: Strategy[Domain]) -> Strategy:
    return to_homogeneous_iterables(elements,
                                    min_size=min_size)


hashables_iterables = min_iterables_sizes.flatmap(partial(to_iterables,
                                                          elements=hashables))
plain_hashables_iterables = (min_iterables_sizes
                             .flatmap(partial(to_iterables,
                                              elements=plain_hashables)))
