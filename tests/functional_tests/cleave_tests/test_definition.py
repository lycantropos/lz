from typing import (Any,
                    Dict,
                    Tuple)

from hypothesis import given

from lz import (left,
                right)
from lz.functional import cleave
from tests.hints import CleavageCall
from tests.utils import (are_iterables_similar,
                         is_empty)
from . import strategies


@given(strategies.positionals_arguments, strategies.keywords_arguments)
def test_base_case(positional_arguments: Tuple[Any, ...],
                   keyword_arguments: Dict[str, Any]) -> None:
    cleavage = cleave()

    result = cleavage(*positional_arguments, **keyword_arguments)

    assert is_empty(result)


@given(strategies.non_empty_cleavage_calls)
def test_step_left(cleavage_call: CleavageCall) -> None:
    (map_, *maps), argument = cleavage_call
    cleavage = cleave(*maps)
    next_cleavage = cleave(*left.attacher(map_)(maps))

    result = cleavage(argument)
    next_result = next_cleavage(argument)

    assert are_iterables_similar(next_result,
                                 left.attacher(map_(argument))(result))


@given(strategies.non_empty_cleavage_calls)
def test_step_right(cleavage_call: CleavageCall) -> None:
    (map_, *maps), argument = cleavage_call
    cleavage = cleave(*maps)
    next_cleavage = cleave(*right.attacher(map_)(maps))

    result = cleavage(argument)
    next_result = next_cleavage(argument)

    assert are_iterables_similar(next_result,
                                 right.attacher(map_(argument))(result))
