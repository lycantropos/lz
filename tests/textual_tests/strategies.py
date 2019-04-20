import os
from typing import (AnyStr,
                    BinaryIO,
                    Tuple)

from hypothesis import strategies

from lz.functional import pack
from tests.hints import (ByteSequence,
                         ByteStreamWithBatchParameters,
                         Strategy)
from tests.strategies import (encodings,
                              to_any_strings,
                              to_byte_sequences,
                              to_byte_streams)
from tests.utils import (to_stream_contents,
                         to_stream_size)


def to_byte_sequences_with_encoding(encoding: str
                                    ) -> Strategy[Tuple[ByteSequence, str]]:
    return strategies.tuples(to_byte_sequences(encoding),
                             strategies.just(encoding))


byte_sequences_with_encodings = (encodings
                                 .flatmap(to_byte_sequences_with_encoding))


def to_strings_with_encoding(encoding: str
                             ) -> Strategy[Tuple[ByteSequence, str]]:
    def decode(byte_sequence: ByteSequence) -> str:
        return byte_sequence.decode(encoding)

    return strategies.tuples(to_byte_sequences(encoding).map(decode),
                             strategies.just(encoding))


strings_with_encodings = encodings.flatmap(to_strings_with_encoding)


def to_separator(any_string: AnyStr) -> Strategy[AnyStr]:
    if not any_string:
        result = os.sep
        if not isinstance(any_string, str):
            result = result.encode()
        return strategies.just(result)
    length = len(any_string)

    def to_start_stop(start: int) -> Strategy[Tuple[int, int]]:
        return strategies.tuples(strategies.just(start),
                                 strategies.integers(start + 1, length))

    return (strategies.integers(0, length - 1)
            .flatmap(to_start_stop)
            .map(pack(slice))
            .map(any_string.__getitem__))


def to_any_string_with_separator(any_string: AnyStr
                                 ) -> Strategy[Tuple[AnyStr, AnyStr]]:
    return strategies.tuples(strategies.just(any_string),
                             to_separator(any_string))


any_strings_with_separators = (encodings.flatmap(to_any_strings)
                               .flatmap(to_any_string_with_separator))


def to_byte_stream_with_batch_parameters(
        byte_stream: BinaryIO) -> Strategy[ByteStreamWithBatchParameters]:
    stream_size = to_stream_size(byte_stream)
    max_batch_size = max(stream_size, 1)
    batches_sizes = strategies.integers(1, max_batch_size)
    batches_end_positions = strategies.integers(0, stream_size)
    return strategies.tuples(strategies.just(byte_stream),
                             strategies.just(to_stream_contents(byte_stream)),
                             strategies.tuples(batches_sizes,
                                               batches_end_positions))


byte_streams_with_batch_parameters = encodings.flatmap(to_byte_streams)
