from hypothesis import given

from lz import (left,
                right)
from lz.replication import duplicate
from tests.hints import LeftFolderCall
from tests.utils import are_objects_similar
from . import strategies


@given(strategies.empty_folder_calls)
def test_base_case(empty_folder_call: LeftFolderCall) -> None:
    projector, initial, empty_iterable = empty_folder_call
    fold = left.folder(projector, initial)

    result = fold(empty_iterable)

    assert result is initial


@given(strategies.non_empty_folder_calls)
def test_step(non_empty_folder_call: LeftFolderCall) -> None:
    projector, initial, non_empty_iterable = non_empty_folder_call
    non_empty_iterator = iter(non_empty_iterable)
    element = next(non_empty_iterator)
    original, target = duplicate(non_empty_iterator)
    fold = left.folder(projector, initial)
    attach = right.attacher(element)

    result = fold(attach(target))

    assert are_objects_similar(result,
                               projector(fold(original), element))
