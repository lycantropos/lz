from typing import (Any,
                    Iterable)

from lz.directed import left
from lz.iterating import first


def test_basic(iterable: Iterable[Any],
               object_: Any) -> None:
    attach = left.attacher(object_)

    result = attach(iterable)

    assert first(result) is object_
