from typing import Any

from lz.functional import identity
from tests.utils import round_trip_pickle


def test_round_trip(object_: Any) -> None:
    result = round_trip_pickle(identity)

    assert result(object_) is object_
