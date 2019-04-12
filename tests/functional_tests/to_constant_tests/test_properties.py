from typing import (Any,
                    Dict,
                    Tuple)

from lz.functional import (curry,
                           to_constant)


def test_currying(object_: Any,
                  positional_arguments: Tuple,
                  keyword_arguments: Dict[str, Any]) -> None:
    constant = to_constant(object_)
    curried_constant = curry(constant)

    result = curried_constant(*positional_arguments, **keyword_arguments)

    assert result is constant(*positional_arguments, **keyword_arguments)
