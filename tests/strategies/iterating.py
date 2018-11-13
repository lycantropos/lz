from typing import (Hashable,
                    Optional)

from hypothesis import strategies

from lz.functional import identity
from lz.hints import Map
from .literals.base import slices


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


def are_slice_indices_none_or_non_negative(slice_: slice) -> bool:
    def is_none_or_non_negative(object_: Optional[int]) -> bool:
        return object_ is None or object_ >= 0

    return (is_none_or_non_negative(slice_.start)
            and is_none_or_non_negative(slice_.stop))


cutter_slices = slices.filter(are_slice_indices_none_or_non_negative)
