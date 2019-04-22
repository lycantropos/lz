from typing import (Any,
                    Iterable)

import pytest
from hypothesis import given

from lz import right
from lz.iterating import last
from tests import strategies


@given(strategies.iterables, strategies.scalars)
def test_basic(iterable: Iterable[Any], object_: Any) -> None:
    attach = right.attacher(object_)

    result = last(attach(iterable))

    assert result is object_


@given(strategies.empty.iterables)
def test_empty_iterable(empty_iterable: Iterable[Any]) -> None:
    with pytest.raises(ValueError):
        last(empty_iterable)
