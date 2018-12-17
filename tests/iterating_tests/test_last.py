from typing import (Any,
                    Iterable)

from lz.iterating import (first,
                          last,
                          reverse)
from lz.replication import duplicate
from tests.utils import are_objects_similar


def test_basic(non_empty_iterable: Iterable[Any]) -> None:
    original, target = duplicate(non_empty_iterable)

    result = last(target)

    assert are_objects_similar(result, first(reverse(original)))
