from typing import Sequence

from hypothesis import given

from lz.typology import subclass_of
from tests.utils import round_trip_pickle
from . import strategies


@given(strategies.pickleable_classes_sequences, strategies.classes)
def test_round_trip(pickleable_classes: Sequence[type],
                    class_: type) -> None:
    function = subclass_of(*pickleable_classes)

    result = round_trip_pickle(function)

    assert result(class_) is function(class_)
