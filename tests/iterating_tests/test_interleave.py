from typing import (Any,
                    Iterable)

from lz import left
from lz.iterating import (first,
                          interleave)
from lz.replication import duplicate
from tests.utils import (are_iterables_similar,
                         are_objects_similar)


def test_basic(empty_iterable: Iterable[Any],
               nested_iterable: Iterable[Iterable[Any]]) -> None:
    original, target = duplicate(nested_iterable)

    result = interleave(left.attacher(empty_iterable)(target))

    assert are_iterables_similar(result, interleave(original))


def test_step(non_empty_iterable: Iterable[Any],
              nested_iterable: Iterable[Iterable[Any]]) -> None:
    original, target = duplicate(non_empty_iterable)

    result = interleave(left.attacher(target)(nested_iterable))

    assert are_objects_similar(first(result), first(original))
