from typing import (Any,
                    Sequence)

from lz.typology import instance_of
from tests.utils import round_trip_pickle


def test_round_trip(pickleable_classes: Sequence[type],
                    object_: Any) -> None:
    function = instance_of(*pickleable_classes)

    result = round_trip_pickle(function)

    assert result(object_) is function(object_)