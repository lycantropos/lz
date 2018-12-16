from typing import (Any,
                    Iterable)

from lz.iterating import header
from lz.replication import duplicate
from tests.utils import (capacity,
                         iterable_starts_with)


def test_capacity(non_empty_iterable: Iterable[Any],
                  natural_number: int) -> None:
    original, target = duplicate(non_empty_iterable)
    head = header(natural_number)

    result = head(target)

    if capacity(original) < natural_number:
        assert capacity(result) < natural_number
    else:
        assert capacity(result) == natural_number


def test_elements(non_empty_iterable: Iterable[Any],
                  natural_number: int) -> None:
    original, target = duplicate(non_empty_iterable)
    head = header(natural_number)

    result = head(target)

    assert iterable_starts_with(original, result)
