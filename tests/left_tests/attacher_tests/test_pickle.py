from typing import (Any,
                    Iterable)

from hypothesis import given

from lz import left
from lz.replication import duplicate
from tests import strategies
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)


@given(strategies.iterables, strategies.objects)
def test_round_trip(iterable: Iterable[Any], object_: Any) -> None:
    original, target = duplicate(iterable)
    attach = left.attacher(object_)

    result = round_trip_pickle(attach)

    assert are_iterables_similar(result(target), attach(original))
