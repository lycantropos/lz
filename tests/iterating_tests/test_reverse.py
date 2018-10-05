from itertools import tee
from typing import (Any,
                    Iterable)

from lz.iterating import reverse
from tests.utils import are_similar


def test_basic(iterable: Iterable[Any]) -> None:
    original, target = tee(iterable)

    result = reverse(target)

    assert are_similar(result, list(original)[::-1])


def test_involution(iterable: Iterable[Any]) -> None:
    original, target = tee(iterable)

    result = reverse(reverse(target))

    assert are_similar(result, original)
