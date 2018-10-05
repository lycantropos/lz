from typing import Any

import pytest

from lz.iterating import expand


def test_basic(object_: Any) -> None:
    result = expand(object_)
    result_iterator = iter(result)

    assert next(result_iterator) is object_

    with pytest.raises(StopIteration):
        next(result_iterator)
