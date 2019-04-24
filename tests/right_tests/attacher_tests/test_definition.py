from typing import (Any,
                    Iterable)

from hypothesis import given

from lz import right
from lz.iterating import last
from tests import strategies


@given(strategies.iterables, strategies.scalars)
def test_basic(iterable: Iterable[Any], object_: Any) -> None:
    attach = right.attacher(object_)

    result = attach(iterable)

    assert last(result) is object_
