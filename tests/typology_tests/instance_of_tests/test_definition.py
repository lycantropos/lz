from typing import (Any,
                    Sequence)

from hypothesis import given

from lz.typology import instance_of
from tests.utils import equivalence
from . import strategies


@given(strategies.scalars)
def test_base_case(object_: Any) -> None:
    result = instance_of()

    assert not result(object_)


@given(strategies.classes_sequences, strategies.classes, strategies.scalars)
def test_step(classes: Sequence[type], class_: type, object_: Any) -> None:
    base_function = instance_of(*classes)
    adjunct_function = instance_of(class_)
    summary_function = instance_of(*classes, class_)

    assert equivalence(summary_function(object_),
                       base_function(object_) or adjunct_function(object_))
