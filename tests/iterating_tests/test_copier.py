from typing import (Any,
                    Iterable)

import pytest

from lz.iterating import copier
from tests.utils import are_iterables_similar


def test_basic(iterable: Iterable[Any],
               positive_capacity: int) -> None:
    copy = copier(positive_capacity)

    result = copy(iterable)

    assert are_iterables_similar(*result)


def test_factory_fail(non_positive_natural_number: int) -> None:
    with pytest.raises(ValueError):
        copier(non_positive_natural_number)
