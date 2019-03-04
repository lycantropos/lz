from typing import (Any,
                    Dict,
                    Sequence,
                    Tuple)

from lz import (left,
                right)
from lz.functional import cleave
from lz.hints import (Domain,
                      Map)
from tests.utils import (are_iterables_similar,
                         is_empty)


def test_base_case(positional_arguments: Tuple[Any, ...],
                   keyword_arguments: Dict[str, Any]) -> None:
    cleft = cleave()

    result = cleft(*positional_arguments, **keyword_arguments)

    assert is_empty(result)


def test_step_left(maps: Sequence[Map],
                   map_: Map,
                   map_argument: Domain) -> None:
    cleft = cleave(*maps)
    next_cleft = cleave(*left.attacher(map_)(maps))

    result = cleft(map_argument)
    next_result = next_cleft(map_argument)

    assert are_iterables_similar(next_result,
                                 left.attacher(map_(map_argument))(result))


def test_step_right(maps: Sequence[Map],
                    map_: Map,
                    map_argument: Domain) -> None:
    cleft = cleave(*maps)
    next_cleft = cleave(*right.attacher(map_)(maps))

    result = cleft(map_argument)
    next_result = next_cleft(map_argument)

    assert are_iterables_similar(next_result,
                                 right.attacher(map_(map_argument))(result))
