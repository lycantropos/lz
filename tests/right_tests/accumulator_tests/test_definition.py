from hypothesis import given

from lz import right
from lz.iterating import (first,
                          last)
from lz.replication import duplicate
from tests.hints import RightAccumulatorCall
from tests.utils import are_objects_similar
from . import strategies


@given(strategies.accumulator_calls)
def test_first(accumulator_call: RightAccumulatorCall) -> None:
    function, initial, sequence = accumulator_call
    accumulate = right.accumulator(function, initial)

    result = accumulate(sequence)

    assert first(result) is initial


@given(strategies.accumulator_calls)
def test_last(accumulator_call: RightAccumulatorCall) -> None:
    function, initial, sequence = accumulator_call
    original, target = duplicate(sequence)
    accumulate = right.accumulator(function, initial)
    fold = right.folder(function, initial)

    result = accumulate(target)

    assert are_objects_similar(last(result), fold(original))
