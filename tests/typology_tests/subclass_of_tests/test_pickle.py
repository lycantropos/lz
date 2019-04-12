from typing import Sequence

from lz.typology import subclass_of
from tests.utils import round_trip_pickle


def test_round_trip(classes: Sequence[type],
                    class_: type) -> None:
    function = subclass_of(*classes)

    result = round_trip_pickle(function)

    assert result(class_) is function(class_)
