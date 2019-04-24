from hypothesis import given

from lz import left
from lz.replication import duplicate
from tests.hints import LeftAccumulatorCall
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.accumulator_calls)
def test_round_trip(accumulator_call: LeftAccumulatorCall) -> None:
    function, initial, iterable = accumulator_call
    original, target = duplicate(iterable)
    accumulate = left.accumulator(function, initial)

    result = round_trip_pickle(accumulate)

    assert are_iterables_similar(result(target), accumulate(original))
