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
    projector, projector_initial, projector_iterable = accumulator_call
    accumulate = left.accumulator(projector, projector_initial)

    result = accumulate(projector_iterable)

    assert first(result) is projector_initial


@given(strategies.accumulator_calls)
def test_last(accumulator_call: LeftAccumulatorCall) -> None:
    projector, projector_initial, projector_iterable = accumulator_call
    original, target = duplicate(projector_iterable)
    accumulate = left.accumulator(projector, projector_initial)
    fold = left.folder(projector, projector_initial)

    result = accumulate(target)

    assert are_objects_similar(last(result), fold(original))
