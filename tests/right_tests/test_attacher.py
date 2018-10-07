from typing import (Any,
                    Iterable)

from lz import right
from lz.iterating import last


def test_basic(iterable: Iterable[Any],
               object_: Any) -> None:
    attach = right.attacher(object_)

    result = attach(iterable)

    assert last(result) is object_
