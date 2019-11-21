from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.replication import replicator
from tests.utils import (are_iterables_similar,
                         is_empty)
from . import strategies


@given(strategies.scalars, strategies.iterables)
def test_base_case(object_: Any, iterable: Iterable[Any]) -> None:
    replicate = replicator(0)
    for target in (object_, iterable):
        result = replicate(target)

        assert is_empty(result)


@given(strategies.scalars, strategies.iterables, strategies.sizes)
def test_step(object_: Any, iterable: Iterable[Any], size: int) -> None:
    replicate = replicator(size + 1)
    for target in (object_, iterable):
        result = replicate(target)
        result_iterator = iter(result)

        assert are_iterables_similar(replicator(size)
                                     (next(result_iterator)),
                                     result_iterator)
