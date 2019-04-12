from typing import (Any,
                    Sequence)

from lz.typology import subclass_of
from tests.utils import equivalence


def test_base_case(class_: Any) -> None:
    result = subclass_of()

    assert not result(class_)


def test_step(classes: Sequence[type],
              class_: type,
              other_class: type) -> None:
    base_function = subclass_of(*classes)
    adjunct_function = subclass_of(class_)
    summary_function = subclass_of(*classes, class_)

    assert equivalence(summary_function(other_class),
                       base_function(other_class)
                       or adjunct_function(other_class))
