from typing import (Any,
                    Iterable)

from lz.iterating import (duplicate,
                          first,
                          last,
                          reverse)


def test_basic(non_empty_iterable: Iterable[Any]) -> None:
    original, target = duplicate(non_empty_iterable)

    result = last(target)

    assert result is first(reverse(original))
