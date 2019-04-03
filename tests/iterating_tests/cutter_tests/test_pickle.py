import pickle
from typing import (Any,
                    Iterable)

from lz.functional import compose
from lz.iterating import cutter
from lz.replication import duplicate
from tests.utils import are_iterables_similar


def test_round_trip(iterable: Iterable[Any],
                    cutter_slice: slice) -> None:
    original, target = duplicate(iterable)
    cut = cutter(cutter_slice)
    make_round_trip = compose(pickle.loads, pickle.dumps)

    result = make_round_trip(cut)

    assert are_iterables_similar(result(target), cut(original))
