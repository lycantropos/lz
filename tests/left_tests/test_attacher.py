from typing import (Any,
                    Iterable)

from lz import left


def test_basic(iterable: Iterable[Any],
               object_: Any) -> None:
    attach = left.attacher(object_)

    result = attach(iterable)
    result_iterator = iter(result)

    assert next(result_iterator) is object_
