from typing import Any

from lz.typology import instance_of
from tests.utils import equivalence


def test_type(class_: type) -> None:
    result = instance_of(class_)

    assert callable(result)


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
