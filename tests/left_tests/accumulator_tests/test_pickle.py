from hypothesis import given

from lz import left
from lz.replication import duplicate
from tests.hints import LeftAccumulatorCall
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.accumulator_calls)
def test_last(accumulator_call: LeftAccumulatorCall) -> None:
    projector, projector_initial, projector_iterable = accumulator_call
    original, target = duplicate(projector_iterable)
    accumulate = left.accumulator(projector, projector_initial)

    result = round_trip_pickle(accumulate)

    assert are_iterables_similar(result(target), accumulate(original))
