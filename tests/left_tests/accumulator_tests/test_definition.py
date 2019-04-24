from hypothesis import given

from lz import left
from lz.iterating import (first,
                          last)
from lz.replication import duplicate
from tests.hints import LeftAccumulatorCall
from tests.utils import are_objects_similar
from . import strategies


@given(strategies.accumulator_calls)
def test_first(accumulator_call: LeftAccumulatorCall) -> None:
    function, initial, iterable = accumulator_call
    accumulate = left.accumulator(function, initial)

    result = accumulate(iterable)

    assert first(result) is initial


@given(strategies.accumulator_calls)
def test_last(accumulator_call: LeftAccumulatorCall) -> None:
    function, initial, iterable = accumulator_call
    original, target = duplicate(iterable)
    accumulate = left.accumulator(function, initial)
    fold = left.folder(function, initial)

    result = accumulate(target)

    assert are_objects_similar(last(result), fold(original))
