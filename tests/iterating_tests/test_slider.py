from itertools import (islice,
                       tee)
from typing import (Any,
                    Iterable)

import pytest

from lz.iterating import slider
from tests.configs import MAX_ITERABLES_SIZE


def test_basic(iterable: Iterable[Any],
               slider_size: int) -> None:
    original, target = tee(iterable)
    slide = slider(slider_size)

    result = slide(target)
    result_iterator = iter(result)

    original_elements = tuple(islice(original, slider_size))
    assert original_elements == next(result_iterator)
    for result_element, original_element in zip(result_iterator, original):
        original_elements = original_elements[1:] + (original_element,)
        assert result_element == original_elements

    with pytest.raises(StopIteration):
        next(original)

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_invalid_size(iterable: Iterable[Any]) -> None:
    invalid_slide = slider(MAX_ITERABLES_SIZE + 1)

    result = invalid_slide(iterable)
    result_iterator = iter(result)

    with pytest.raises(ValueError):
        next(result_iterator)
