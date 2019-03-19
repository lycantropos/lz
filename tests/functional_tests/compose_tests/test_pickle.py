import pickle
from typing import Sequence

from lz.functional import compose
from lz.hints import Map


def test_round_trip(various_suitable_maps: Sequence[Map]) -> None:
    composition = compose(*various_suitable_maps)

    pickled = pickle.dumps(composition)

    assert pickle.loads(pickled) == composition
