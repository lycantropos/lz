import inspect
from typing import (Any,
                    Sequence)

from lz.typology import instance_of
from tests.utils import equivalence


def test_type(class_: type) -> None:
    result = instance_of(class_)

    assert callable(result)


def test_signature(class_: type) -> None:
    result = instance_of(class_)

    signature = inspect.signature(result)

    assert len(signature.parameters) == 1


def test_result_type(class_: type,
                     object_: Any) -> None:
    function = instance_of(class_)

    result = function(object_)

    assert isinstance(result, bool)


def test_basic(object_: Any) -> None:
    result = instance_of(type(object_))

    assert result(object_)


def test_commutativity(class_: type, other_class: type, object_: Any) -> None:
    left_function = instance_of(class_, other_class)
    right_function = instance_of(other_class, class_)

    assert equivalence(left_function(object_), right_function(object_))


def test_base_case(object_: Any) -> None:
    result = instance_of()

    assert not result(object_)


def test_step(classes: Sequence[type], class_: type, object_: Any) -> None:
    base_function = instance_of(*classes)
    adjunct_function = instance_of(class_)
    summary_function = instance_of(*classes, class_)

    assert equivalence(summary_function(object_),
                       base_function(object_) or adjunct_function(object_))
