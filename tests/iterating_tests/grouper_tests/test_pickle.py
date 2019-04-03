import pickle
from typing import (Any,
                    Hashable,
                    Iterable)

from lz.functional import compose
from lz.hints import Map
from lz.iterating import grouper
from lz.replication import duplicate
from tests.utils import are_iterables_similar


def test_round_trip(plain_hashables_iterable: Iterable[Hashable],
                    grouper_key: Map[Any, Hashable]) -> None:
    original, target = duplicate(plain_hashables_iterable)
    group_by = grouper(grouper_key)
    make_round_trip = compose(pickle.loads, pickle.dumps)

    result = make_round_trip(group_by)

    assert are_iterables_similar(result(target), group_by(original))
