from typing import (Any,
                    Iterable)

from lz.iterating import first
from lz.replication import replicator
from tests.utils import (are_iterables_similar,
                         is_empty)


def test_base_case(object_: Any,
                   iterable: Iterable[Any]) -> None:
    replicate = replicator(0)
    for target in (object_, iterable):
        result = replicate(target)

        assert is_empty(result)


def test_step(object_: Any,
              iterable: Iterable[Any],
              replicator_size: int) -> None:
    replicate = replicator(replicator_size + 1)
    for target in (object_, iterable):
        result = replicate(target)
        result_iterator = iter(result)

        assert are_iterables_similar(replicator(replicator_size)
                                     (first(result_iterator)),
                                     result_iterator)
