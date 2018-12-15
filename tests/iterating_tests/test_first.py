from typing import (Any,
                    Iterable)

from lz.iterating import (duplicate,
                          first)


def test_basic(non_empty_iterable: Iterable[Any]) -> None:
    original, target = duplicate(non_empty_iterable)

    result = first(target)

    assert result is next(original)
