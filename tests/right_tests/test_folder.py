from itertools import tee
from typing import (Callable,
                    Iterable)

from lz import (left,
                right)
from lz.hints import (Domain,
                      Range)


def test_base_case(projector: Callable[[Domain, Range], Range],
                   projector_initial: Range,
                   empty_iterable: Iterable[Domain]) -> None:
    fold = right.folder(projector, projector_initial)

    result = fold(empty_iterable)

    assert result is projector_initial


def test_step(projector: Callable[[Domain, Range], Range],
              projector_initial: Range,
              projector_iterable: Iterable[Domain],
              projector_domain_element: Domain) -> None:
    first_target, second_target = tee(projector_iterable)
    fold = right.folder(projector, projector_initial)
    attach = left.attacher(projector_domain_element)

    result = fold(first_target)
    next_result = fold(attach(second_target))

    assert next_result == projector(projector_domain_element, result)
