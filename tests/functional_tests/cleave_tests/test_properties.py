from collections import abc

from hypothesis import given

from lz.functional import (cleave,
                           curry)
from tests.hints import CleavageCall
from tests.utils import are_iterables_similar
from . import strategies


@given(strategies.cleavage_calls)
def test_currying(cleavage_call: CleavageCall) -> None:
    maps, argument = cleavage_call
    cleavage = cleave(*maps)
    curried_cleavage = curry(cleavage)

    result = curried_cleavage(argument)

    assert isinstance(result, abc.Iterable)
    assert are_iterables_similar(result, cleavage(argument))
