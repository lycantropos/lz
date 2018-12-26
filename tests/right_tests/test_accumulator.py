from typing import (Callable,
                    Sequence)

from lz import right
from lz.hints import (Domain,
                      Range)
from lz.iterating import (first,
                          last)
from lz.replication import duplicate
from tests.utils import are_objects_similar


def test_first(projector: Callable[[Domain, Range], Range],
               projector_initial: Range,
               projector_sequence: Sequence[Domain]) -> None:
    accumulate = right.accumulator(projector, projector_initial)

    result = accumulate(projector_sequence)

    assert first(result) is projector_initial


def test_last(projector: Callable[[Domain, Range], Range],
              projector_initial: Range,
              projector_sequence: Sequence[Domain]) -> None:
    first_target, second_target = duplicate(projector_sequence)
    accumulate = right.accumulator(projector, projector_initial)
    fold = right.folder(projector, projector_initial)

    result = accumulate(first_target)
    fold_result = fold(second_target)

    assert are_objects_similar(last(result), fold_result)
