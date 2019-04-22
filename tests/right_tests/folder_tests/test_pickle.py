from hypothesis import given

from lz import right
from lz.replication import duplicate
from tests.hints import RightFolderCall
from tests.utils import round_trip_pickle
from . import strategies


@given(strategies.folder_calls)
def test_round_trip(folder_call: RightFolderCall) -> None:
    function, initial, iterable = folder_call
    original, target = duplicate(iterable)
    fold = right.folder(function, initial)

    result = round_trip_pickle(fold)

    assert result(target) == fold(original)
