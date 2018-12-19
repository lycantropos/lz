from typing import Hashable

from hypothesis import strategies

from lz.functional import identity
from lz.hints import Map
from tests.configs import MAX_ITERABLES_SIZE


def to_grouper_key(odd_order: int) -> Map[Hashable, Hashable]:
    def grouper_key(object_: Hashable) -> Hashable:
        return hash(object_) ** odd_order

    return grouper_key


def is_odd(number: int) -> bool:
    return bool(number & 1)


groupers_keys = (strategies.integers(1, 1000)
                 .filter(is_odd)
                 .map(to_grouper_key)
                 | strategies.just(identity))
non_negative_indices = strategies.integers(0, MAX_ITERABLES_SIZE - 1)
positive_indices = strategies.integers(1, MAX_ITERABLES_SIZE - 1)
non_negative_slices_fields = strategies.none() | non_negative_indices
non_negative_slices = strategies.builds(slice,
                                        non_negative_slices_fields,
                                        non_negative_slices_fields,
                                        strategies.none() | positive_indices)
