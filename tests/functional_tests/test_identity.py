from typing import Any

from lz.functional import identity


def test_basic(object_: Any) -> None:
    result = identity(object_)

    assert result is object_
