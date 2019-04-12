from typing import (Any,
                    Sequence)

from lz.typology import instance_of
from tests.utils import equivalence


def test_base_case(object_: Any) -> None:
    result = instance_of()

    assert not result(object_)


def test_step(classes: Sequence[type], class_: type, object_: Any) -> None:
    base_function = instance_of(*classes)
    adjunct_function = instance_of(class_)
    summary_function = instance_of(*classes, class_)

    assert equivalence(summary_function(object_),
                       base_function(object_) or adjunct_function(object_))
