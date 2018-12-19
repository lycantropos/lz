from typing import (Any,
                    Iterable)

from lz.iterating import trailer
from lz.replication import duplicate
from tests.utils import (capacity,
                         iterable_ends_with)


def test_capacity(non_empty_iterable: Iterable[Any],
                  natural_number: int) -> None:
    original, target = duplicate(non_empty_iterable)
    trail = trailer(natural_number)

    result = trail(target)

    if capacity(original) < natural_number:
        assert capacity(result) < natural_number
    else:
        assert capacity(result) == natural_number


def test_elements(non_empty_iterable: Iterable[Any],
                  natural_number: int) -> None:
    original, target = duplicate(non_empty_iterable)
    trail = trailer(natural_number)

    result = trail(target)

    assert iterable_ends_with(original, result)
