from hypothesis import given

from lz.functional import cleave
from tests.hints import CleavageCall
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.cleavage_calls)
def test_round_trip(cleavage_call: CleavageCall) -> None:
    maps, argument = cleavage_call
    cleavage = cleave(*maps)

    result = round_trip_pickle(cleavage)

    assert are_iterables_similar(result(argument), cleavage(argument))
