from typing import (Any,
                    BinaryIO,
                    Iterable,
                    Set,
                    TextIO)

from lz import (left,
                right)
from lz.iterating import (first,
                          last,
                          reverse)
from lz.replication import duplicate
from lz.textual import encoder
from tests.utils import (are_iterables_similar,
                         is_empty)


def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = reverse(empty_iterable)

    assert is_empty(result)


def test_step_right(iterable: Iterable[Any],
                    object_: Any) -> None:
    attach = right.attacher(object_)

    result = reverse(attach(iterable))

    assert first(result) is object_


def test_step_left(iterable: Iterable[Any],
                   object_: Any) -> None:
    attach = left.attacher(object_)

    result = reverse(attach(iterable))

    assert last(result) is object_


def test_involution(iterable: Iterable[Any]) -> None:
    original, target = duplicate(iterable)

    result = reverse(reverse(target))

    assert are_iterables_similar(result, original)


def test_byte_stream(byte_stream: BinaryIO,
                     byte_stream_batch_size: int,
                     byte_stream_contents: bytes,
                     byte_stream_lines_separator: bytes,
                     keep_separator: bool) -> None:
    result = reverse(byte_stream,
                     batch_size=byte_stream_batch_size,
                     lines_separator=byte_stream_lines_separator,
                     keep_lines_separator=keep_separator)

    assert are_byte_substrings(result, byte_stream_contents)


def test_text_stream(encoding: str,
                     text_stream: TextIO,
                     text_stream_batch_size: int,
                     text_stream_raw_contents: bytes,
                     text_stream_lines_separator: str,
                     keep_separator: bool) -> None:
    result = reverse(text_stream,
                     batch_size=text_stream_batch_size,
                     lines_separator=text_stream_lines_separator,
                     keep_lines_separator=keep_separator)

    assert are_byte_substrings(map(encoder(encoding), result),
                               text_stream_raw_contents)


def are_byte_substrings(byte_strings: Iterable[bytes],
                        target_string: bytes) -> bool:
    def to_tolerance_level(unique_characters: Set[int]) -> float:
        return 0.8 * max(len(unique_characters) - 1, 0)

    return all(len(set(target_string) & set(line))
               >= to_tolerance_level(set(target_string))
               for line in byte_strings)
