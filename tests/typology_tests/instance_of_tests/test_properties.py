from typing import Any

from hypothesis import given

from lz.typology import instance_of
from tests.utils import equivalence
from . import strategies


@given(strategies.classes)
def test_type(class_: type) -> None:
    result = instance_of(class_)

    assert callable(result)


@given(strategies.classes, strategies.scalars)
def test_result_type(class_: type, object_: Any) -> None:
    function = instance_of(class_)

    result = function(object_)

    assert isinstance(result, bool)


@given(strategies.scalars)
def test_basic(object_: Any) -> None:
    result = instance_of(type(object_))

    assert result(object_)


@given(strategies.classes, strategies.classes, strategies.scalars)
def test_commutativity(class_: type, other_class: type, object_: Any) -> None:
    left_function = instance_of(class_, other_class)
    right_function = instance_of(other_class, class_)

    assert equivalence(left_function(object_), right_function(object_))
