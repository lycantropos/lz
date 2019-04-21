from typing import (Any,
                    Iterable)

from hypothesis import given

from lz import left
from lz.iterating import first
from tests import strategies


@given(strategies.iterables, strategies.objects)
def test_basic(iterable: Iterable[Any], object_: Any) -> None:
    attach = left.attacher(object_)

    result = attach(iterable)

    assert first(result) is object_
