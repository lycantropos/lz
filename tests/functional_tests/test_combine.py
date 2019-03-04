from typing import (Any,
                    Sequence,
                    Tuple)

from lz import (left,
                right)
from lz.functional import combine
from lz.hints import (Domain,
                      Map)
from tests.utils import (are_iterables_similar,
                         is_empty)


def test_base_case(positional_arguments: Tuple[Any, ...]) -> None:
    combined = combine()

    result = combined(positional_arguments)

    assert is_empty(result)


def test_step_left(maps: Sequence[Map],
                   map_: Map,
                   maps_arguments: Sequence[Domain],
                   map_argument: Domain) -> None:
    combined = combine(*maps)
    next_combined = combine(*left.attacher(map_)(maps))

    result = combined(maps_arguments)
    next_result = next_combined(left.attacher(map_argument)(maps_arguments))

    assert are_iterables_similar(next_result,
                                 left.attacher(map_(map_argument))(result))


def test_step_right(maps: Sequence[Map],
                    map_: Map,
                    maps_arguments: Sequence[Domain],
                    map_argument: Domain) -> None:
    combined = combine(*maps)
    next_combined = combine(*right.attacher(map_)(maps))

    result = combined(maps_arguments)
    next_result = next_combined(right.attacher(map_argument)(maps_arguments))

    assert are_iterables_similar(next_result,
                                 right.attacher(map_(map_argument))(result))
