from functools import partial
from typing import (Callable,
                    Hashable)

from hypothesis import strategies

from lz.functional import identity
from tests.strategies import (scalars,
                              to_homogeneous_iterables)


def grouper_key(object_: Hashable,
                odd_order: int = 1) -> Hashable:
    return hash(object_) ** odd_order


def to_key_function(odd_order: int) -> Callable[[Hashable], Hashable]:
    return partial(grouper_key,
                   odd_order=odd_order)


def is_odd(number: int) -> bool:
    return bool(number & 1)


keys_functions = (strategies.sampled_from(range(1, 1000, 2))
                  .map(to_key_function)
                  | strategies.just(identity))
hashables_iterables = to_homogeneous_iterables(scalars)
