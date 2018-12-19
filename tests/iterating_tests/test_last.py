from typing import (Any,
                    Iterable)

from lz import right
from lz.iterating import last


def test_basic(iterable: Iterable[Any],
               object_: Any) -> None:
    attach = right.attacher(object_)

    result = last(attach(iterable))

    assert result is object_
