from typing import (Any,
                    Tuple)

from hypothesis import given

from lz import (left,
                right)
from lz.functional import combine
from tests.hints import CombinationCall
from tests.utils import (are_iterables_similar,
                         is_empty)
from . import strategies


@given(strategies.positionals_arguments)
def test_base_case(positional_arguments: Tuple[Any, ...]) -> None:
    combination = combine()

    result = combination(positional_arguments)

    assert is_empty(result)


@given(strategies.non_empty_combination_calls)
def test_step_left(combination_call: CombinationCall) -> None:
    (map_, *rest_maps), (argument, *rest_arguments) = combination_call
    combination = combine(*rest_maps)
    next_combination = combine(*left.attacher(map_)(rest_maps))

    result = combination(rest_arguments)
    next_result = next_combination(left.attacher(argument)(rest_arguments))

    assert are_iterables_similar(next_result,
                                 left.attacher(map_(argument))(result))


@given(strategies.non_empty_combination_calls)
def test_step_right(combination_call: CombinationCall) -> None:
    (map_, *rest_maps), (argument, *rest_arguments) = combination_call
    combination = combine(*rest_maps)
    next_combination = combine(*right.attacher(map_)(rest_maps))

    result = combination(rest_arguments)
    next_result = next_combination(right
                                   .attacher(argument)(rest_arguments))

    assert are_iterables_similar(next_result,
                                 right.attacher(map_(argument))(result))
