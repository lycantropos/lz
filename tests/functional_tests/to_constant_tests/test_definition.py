from typing import (Any,
                    Dict,
                    Tuple)

from hypothesis import given

from lz.functional import to_constant
from tests import strategies


@given(strategies.objects,
       strategies.positionals_arguments,
       strategies.keywords_arguments)
def test_basic(object_: Any,
               positional_arguments: Tuple,
               keyword_arguments: Dict[str, Any]) -> None:
    constant = to_constant(object_)

    result = constant(*positional_arguments, **keyword_arguments)

    assert result is object_
