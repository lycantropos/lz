from typing import Any

from hypothesis import given

from lz.functional import (curry,
                           identity)
from tests import strategies


@given(strategies.scalars)
def test_currying(object_: Any) -> None:
    curried = curry(identity)

    result = curried(object_)

    assert result is object_
