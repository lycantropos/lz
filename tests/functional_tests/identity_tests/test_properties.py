from typing import Any

from lz.functional import (curry,
                           identity)


def test_currying(object_: Any) -> None:
    curried = curry(identity)

    result = curried(object_)

    assert result is object_
