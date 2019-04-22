from typing import (Any,
                    Iterable)

import pytest
from hypothesis import given

from lz.iterating import (expand,
                          first)
from lz.replication import duplicate
from tests import strategies
from tests.utils import iterable_starts_with


@given(strategies.non_empty_iterables)
def test_basic(non_empty_iterable: Iterable[Any]) -> None:
    original, target = duplicate(non_empty_iterable)

    result = first(target)

    assert iterable_starts_with(original, expand(result))


@given(strategies.empty.iterables)
def test_empty_iterable(empty_iterable: Iterable[Any]) -> None:
    with pytest.raises(ValueError):
        first(empty_iterable)
