from hypothesis import given

from lz import right
from lz.replication import duplicate
from tests.hints import RightAccumulatorCall
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.accumulator_calls)
def test_round_trip(accumulator_call: RightAccumulatorCall) -> None:
    function, initial, sequence = accumulator_call
    original, target = duplicate(sequence)
    accumulate = right.accumulator(function, initial)

    result = round_trip_pickle(accumulate)

    assert are_iterables_similar(result(target), accumulate(original))
