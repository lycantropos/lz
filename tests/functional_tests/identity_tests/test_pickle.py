from typing import Any

from hypothesis import given

from lz.functional import identity
from tests import strategies
from tests.utils import round_trip_pickle


@given(strategies.scalars)
def test_round_trip(object_: Any) -> None:
    result = round_trip_pickle(identity)

    assert result(object_) is object_
