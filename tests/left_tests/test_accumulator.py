from itertools import tee
from typing import (Callable,
                    Iterable)

from lz import left
from lz.hints import (Domain,
                      Range)
from lz.iterating import (first,
                          last)


def test_first(projector: Callable[[Range, Domain], Range],
               projector_initial: Range,
               projector_iterable: Iterable[Domain]) -> None:
    accumulate = left.accumulator(projector, projector_initial)

    result = accumulate(projector_iterable)

    assert first(result) is projector_initial


def test_last(projector: Callable[[Range, Domain], Range],
              projector_initial: Range,
              projector_iterable: Iterable[Domain]) -> None:
    first_target, second_target = tee(projector_iterable)
    accumulate = left.accumulator(projector, projector_initial)
    fold = left.folder(projector, projector_initial)

    result = accumulate(first_target)
    fold_result = fold(second_target)

    assert last(result) == fold_result
