import pickle
from typing import (Any,
                    Iterable)

from lz.functional import compose
from lz.iterating import slider
from lz.replication import duplicate
from tests.utils import are_iterables_similar


def test_round_trip(iterable: Iterable[Any],
                    size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(size)
    make_round_trip = compose(pickle.loads, pickle.dumps)

    result = make_round_trip(slide)

    assert are_iterables_similar(result(target), slide(original))
