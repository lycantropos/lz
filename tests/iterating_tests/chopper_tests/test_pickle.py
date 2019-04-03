import pickle
from typing import (Any,
                    Iterable)

from lz.functional import compose
from lz.iterating import chopper
from lz.replication import duplicate
from tests.utils import are_iterables_similar


def test_round_trip(iterable: Iterable[Any],
                    size: int) -> None:
    original, target = duplicate(iterable)
    chop = chopper(size)
    make_round_trip = compose(pickle.loads, pickle.dumps)

    result = make_round_trip(chop)

    assert are_iterables_similar(result(target), chop(original))
