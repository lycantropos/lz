from hypothesis import given

from lz import (left,
                right)
from lz.replication import duplicate
from tests.hints import RightFolderCall
from tests.utils import are_objects_similar
from . import strategies


@given(strategies.empty_folder_calls)
def test_base_case(empty_folder_call: RightFolderCall) -> None:
    function, initial, empty_sequence = empty_folder_call
    fold = right.folder(function, initial)

    result = fold(empty_sequence)

    assert result is initial


@given(strategies.non_empty_folder_calls)
def test_step(non_empty_folder_call: RightFolderCall) -> None:
    function, initial, non_empty_sequence = non_empty_folder_call
    element, sequence = non_empty_sequence[0], non_empty_sequence[1:]
    original, target = duplicate(sequence)
    fold = right.folder(function, initial)
    attach = left.attacher(element)

    result = fold(attach(target))

    assert are_objects_similar(result, function(element, fold(original)))
