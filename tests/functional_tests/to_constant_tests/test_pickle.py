from typing import (Any,
                    Dict,
                    Tuple)

from lz.functional import to_constant
from tests.utils import (are_objects_similar,
                         round_trip_pickle)


def test_round_trip(pickleable_object: Any,
                    positional_arguments: Tuple,
                    keyword_arguments: Dict[str, Any]) -> None:
    constant = to_constant(pickleable_object)

    result = round_trip_pickle(constant)

    assert are_objects_similar(result(*positional_arguments,
                                      **keyword_arguments),
                               constant(*positional_arguments,
                                        **keyword_arguments))
