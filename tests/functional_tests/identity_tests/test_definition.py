from typing import Any

from hypothesis import given

from lz.functional import identity
from tests import strategies


@given(strategies.objects)
def test_basic(object_: Any) -> None:
    result = identity(object_)

    assert result is object_
