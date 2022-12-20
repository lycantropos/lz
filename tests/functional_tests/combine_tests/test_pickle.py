from hypothesis import given

from lz.functional import combine
from tests.hints import CombinationCall
from tests.utils import (are_iterables_similar,
                         round_trip_pickle)
from . import strategies


@given(strategies.combinations_calls)
def test_round_trip(combination_call: CombinationCall) -> None:
    maps, arguments = combination_call
    combination = combine(*maps)

    result = round_trip_pickle(combination)

    assert are_iterables_similar(result(*arguments),
                                 combination(*arguments))
