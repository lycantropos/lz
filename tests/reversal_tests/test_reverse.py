from collections import abc
from typing import (Any,
                    Sequence)

import pytest
from hypothesis import given

from lz.iterating import (first,
                          last)
from lz.replication import duplicate
from lz.reversal import reverse
from tests.hints import (ByteSequence,
                         StreamWithReverseParameters)
from tests.utils import (are_iterables_similar,
                         are_objects_similar,
                         is_empty)
from . import strategies


@given(strategies.empty_sequences)
def test_empty(empty_sequence: Sequence[Any]) -> None:
    result = reverse(empty_sequence)

    assert is_empty(result)


@given(strategies.non_empty_sequences)
def test_non_empty_left_end(non_empty_sequence: Sequence[Any]) -> None:
    original, target = duplicate(non_empty_sequence)

    result = reverse(target)

    assert are_objects_similar(last(result), first(original))


@given(strategies.non_empty_sequences)
def test_non_empty_right_end(non_empty_sequence: Sequence[Any]) -> None:
    original, target = duplicate(non_empty_sequence)

    result = reverse(target)

    assert are_objects_similar(first(result), last(original))


@given(strategies.sequences)
def test_involution(sequence: Sequence[Any]) -> None:
    original, target = duplicate(sequence)

    result = reverse(reverse(target))

    assert are_iterables_similar(result, original)


@given(strategies.byte_streams_with_reverse_parameters)
def test_byte_stream(
        stream_with_reverse_parameters: StreamWithReverseParameters[bytes]
) -> None:
    (stream, contents,
     (batch_size,
      lines_separator,
      keep_separator)) = stream_with_reverse_parameters
    result = reverse(stream,
                     batch_size=batch_size,
                     lines_separator=lines_separator,
                     keep_lines_separator=keep_separator)

    assert isinstance(result, abc.Iterable)
    assert all(remove_newline_characters_from_byte_sequence(line)
               in remove_newline_characters_from_byte_sequence(contents)
               for line in result)


@given(strategies.text_streams_with_reverse_parameters)
def test_text_stream(
        text_stream_with_reverse_parameters: StreamWithReverseParameters[str]
) -> None:
    (stream, contents,
     (batch_size,
      lines_separator,
      keep_separator)) = text_stream_with_reverse_parameters
    result = reverse(stream,
                     batch_size=batch_size,
                     lines_separator=lines_separator,
                     keep_lines_separator=keep_separator)

    assert isinstance(result, abc.Iterable)
    assert all(remove_newline_characters_from_string(line)
               in remove_newline_characters_from_string(contents)
               for line in result)


def remove_newline_characters_from_byte_sequence(byte_sequence: ByteSequence
                                                 ) -> str:
    return byte_sequence.translate(None, b'\r\n')


def remove_newline_characters_from_string(string: str) -> str:
    return string.translate(str.maketrans({'\r': None, '\n': None}))


@given(strategies.irreversible_objects)
def test_unsupported_type(irreversible_object: Any) -> None:
    with pytest.raises(TypeError):
        reverse(irreversible_object)
