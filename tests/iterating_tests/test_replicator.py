from typing import Any

from lz.iterating import first
from lz.replication import replicator
from tests.utils import (are_iterables_similar,
                         is_empty)


def test_base_case(object_: Any) -> None:
    replicate = replicator(0)

    result = replicate(object_)

    assert is_empty(result)


def test_step(object_: Any,
              positive_replicator_size: int) -> None:
    replicate = replicator(positive_replicator_size)

    result = replicate(object_)
    result_iterator = iter(result)

    assert are_iterables_similar(replicator(positive_replicator_size - 1)
                                 (first(result_iterator)),
                                 result_iterator)
