from typing import (Any,
                    Dict,
                    Tuple)

from hypothesis import given

from lz.functional import to_constant
from tests import strategies
from tests.utils import (are_objects_similar,
                         round_trip_pickle)


@given(strategies.scalars,
       strategies.positionals_arguments,
       strategies.keywords_arguments)
def test_round_trip(object_: Any,
                    positional_arguments: Tuple,
                    keyword_arguments: Dict[str, Any]) -> None:
    constant = to_constant(object_)

    result = round_trip_pickle(constant)

    assert are_objects_similar(result(*positional_arguments,
                                      **keyword_arguments),
                               constant(*positional_arguments,
                                        **keyword_arguments))
