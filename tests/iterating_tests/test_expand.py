from typing import Any

import pytest
from hypothesis import given

from lz.iterating import expand
from tests import strategies


@given(strategies.scalars)
def test_basic(object_: Any) -> None:
    result = expand(object_)
    result_iterator = iter(result)

    assert next(result_iterator) is object_

    with pytest.raises(StopIteration):
        next(result_iterator)
