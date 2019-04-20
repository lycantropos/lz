from hypothesis import given

from lz.typology import subclass_of
from tests.utils import equivalence
from . import strategies


@given(strategies.classes)
def test_type(class_: type) -> None:
    result = subclass_of(class_)

    assert callable(result)


@given(strategies.classes, strategies.classes)
def test_result_type(class_: type, other_class: type) -> None:
    function = subclass_of(class_)

    result = function(other_class)

    assert isinstance(result, bool)


@given(strategies.classes)
def test_basic(class_: type) -> None:
    result = subclass_of(class_)

    assert result(class_)


@given(strategies.classes, strategies.classes, strategies.classes)
def test_commutativity(class_: type,
                       other_class: type,
                       another_class: type) -> None:
    left_function = subclass_of(class_, other_class)
    right_function = subclass_of(other_class, class_)

    assert equivalence(left_function(another_class),
                       right_function(another_class))
