from typing import Hashable

from hypothesis import strategies

from lz.functional import identity
from lz.hints import Map


def to_grouper_key(odd_order: int) -> Map[Hashable, Hashable]:
    def grouper_key(object_: Hashable) -> Hashable:
        return hash(object_) ** odd_order

    return grouper_key


def is_odd(number: int) -> bool:
    return bool(number & 1)


groupers_keys = (strategies.just(identity)
                 | strategies.integers(1).filter(is_odd).map(to_grouper_key))
