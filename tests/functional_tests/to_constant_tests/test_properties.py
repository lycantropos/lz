from typing import (Any,
                    Dict,
                    Tuple)

from hypothesis import given

from lz.functional import (curry,
                           to_constant)
from tests import strategies


@given(strategies.objects,
       strategies.positionals_arguments,
       strategies.keywords_arguments)
def test_currying(object_: Any,
                  positional_arguments: Tuple,
                  keyword_arguments: Dict[str, Any]) -> None:
    constant = to_constant(object_)
    curried_constant = curry(constant)

    result = curried_constant(*positional_arguments, **keyword_arguments)

    assert result is constant(*positional_arguments, **keyword_arguments)
