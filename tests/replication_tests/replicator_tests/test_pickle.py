from itertools import islice
from typing import (Any,
                    Iterable)

from hypothesis import given

from lz.replication import replicator
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.scalars, strategies.iterables, strategies.sizes)
def test_round_trip(object_: Any, iterable: Iterable[Any], size: int) -> None:
    for target in (object_, iterable):
        replicate = replicator(size + 1)

        result = round_trip_pickle(replicate)

        result_call = result(target)
        result_call_iterator = iter(result_call)

        assert are_iterables_similar(
                islice(replicate(next(result_call_iterator)), size),
                result_call_iterator)
