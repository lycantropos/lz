from typing import (Any,
                    Dict,
                    Tuple)

from lz.functional import to_constant


def test_basic(object_: Any,
               positional_arguments: Tuple,
               keyword_arguments: Dict[str, Any]) -> None:
    constant = to_constant(object_)

    result = constant(*positional_arguments, **keyword_arguments)

    assert result is object_
