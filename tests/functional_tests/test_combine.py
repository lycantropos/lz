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
    combination = combine()

    result = combination(positional_arguments)

    assert is_empty(result)


def test_step_left(maps: Sequence[Map],
                   map_: Map,
                   maps_arguments: Sequence[Domain],
                   map_argument: Domain) -> None:
    combination = combine(*maps)
    next_combination = combine(*left.attacher(map_)(maps))

    result = combination(maps_arguments)
    next_result = next_combination(left.attacher(map_argument)(maps_arguments))

    assert are_iterables_similar(next_result,
                                 left.attacher(map_(map_argument))(result))


def test_step_right(maps: Sequence[Map],
                    map_: Map,
                    maps_arguments: Sequence[Domain],
                    map_argument: Domain) -> None:
    combination = combine(*maps)
    next_combination = combine(*right.attacher(map_)(maps))

    result = combination(maps_arguments)
    next_result = next_combination(right
                                   .attacher(map_argument)(maps_arguments))

    assert are_iterables_similar(next_result,
                                 right.attacher(map_(map_argument))(result))
