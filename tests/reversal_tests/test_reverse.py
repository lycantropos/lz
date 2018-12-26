from functools import partial
from typing import (Any,
                    BinaryIO,
                    Iterable,
                    Sequence,
                    TextIO)

from lz.iterating import (first,
                          last)
from lz.replication import duplicate
from lz.reversal import reverse
from lz.textual import encoder
from tests.utils import (are_iterables_similar,
                         are_objects_similar,
                         is_empty)


def test_empty(empty_sequence: Sequence[Any]) -> None:
    result = reverse(empty_sequence)

    assert is_empty(result)


limit_min_size = partial(partial,
                         min_size=1)


def test_non_empty_left_end(non_empty_sequence: Sequence[Any]) -> None:
    original, target = duplicate(non_empty_sequence)

    result = reverse(target)

    assert are_objects_similar(last(result), first(original))


def test_non_empty_right_end(non_empty_sequence: Sequence[Any]) -> None:
    original, target = duplicate(non_empty_sequence)

    result = reverse(target)

    assert are_objects_similar(first(result), last(original))


def test_involution(sequence: Sequence[Any]) -> None:
    original, target = duplicate(sequence)

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
    if not target_string:
        return True
    return all(not line or set(line) & set(target_string)
               for line in byte_strings)
