from collections import abc

from hypothesis import given

from lz.functional import (combine,
                           curry)
from tests.hints import CombinationCall
from tests.utils import are_iterables_similar
from . import strategies


@given(strategies.combinations_calls)
def test_currying(combination_call: CombinationCall) -> None:
    maps, arguments = combination_call
    combination = combine(*maps)
    curried_combination = curry(combination)

    result = curried_combination(*arguments)

    assert isinstance(result, abc.Iterable)
    assert are_iterables_similar(result, combination(*arguments))
