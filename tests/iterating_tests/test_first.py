from typing import (Any,
                    Iterable)

from lz.iterating import (expand,
                          first)
from lz.replication import duplicate
from tests.utils import iterable_starts_with


def test_basic(non_empty_iterable: Iterable[Any]) -> None:
    original, target = duplicate(non_empty_iterable)

    result = first(target)

    assert iterable_starts_with(original, expand(result))
