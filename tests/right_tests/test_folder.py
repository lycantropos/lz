from typing import (Callable,
                    Sequence)

from lz import (left,
                right)
from lz.hints import (Domain,
                      Range)
from lz.replication import duplicate
from tests.utils import are_objects_similar


def test_base_case(projector: Callable[[Domain, Range], Range],
                   projector_initial: Range,
                   empty_sequence: Sequence[Domain]) -> None:
    fold = right.folder(projector, projector_initial)

    result = fold(empty_sequence)

    assert result is projector_initial


def test_step(projector: Callable[[Domain, Range], Range],
              projector_initial: Range,
              projector_sequence: Sequence[Domain],
              projector_domain_element: Domain) -> None:
    first_target, second_target = duplicate(projector_sequence)
    original, target = duplicate(projector_domain_element)
    fold = right.folder(projector, projector_initial)
    attach = left.attacher(target)

    result = fold(first_target)
    next_result = fold(attach(second_target))

    assert are_objects_similar(next_result,
                               projector(original, result))
