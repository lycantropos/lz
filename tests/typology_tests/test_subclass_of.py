import inspect
from typing import (Any,
                    Sequence)

from lz.typology import subclass_of
from tests.utils import equivalence


def test_type(class_: type) -> None:
    result = subclass_of(class_)

    assert callable(result)


def test_signature(class_: type) -> None:
    result = subclass_of(class_)

    signature = inspect.signature(result)

    assert len(signature.parameters) == 1


def test_result_type(class_: type,
                     other_class: type) -> None:
    function = subclass_of(class_)

    result = function(other_class)

    assert isinstance(result, bool)


def test_basic(class_: type) -> None:
    result = subclass_of(class_)

    assert result(class_)


def test_commutativity(class_: type,
                       other_class: type,
                       another_class: type) -> None:
    left_function = subclass_of(class_, other_class)
    right_function = subclass_of(other_class, class_)

    assert equivalence(left_function(another_class),
                       right_function(another_class))


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
