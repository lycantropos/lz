from typing import (BinaryIO,
                    Tuple)

from hypothesis import strategies

from tests.hints import (ByteSequence,
                         ByteStreamWithBatchParameters,
                         Strategy)
from tests.strategies import (encodings,
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


byte_streams_with_batch_parameters = (
    encodings.flatmap(to_byte_streams).flatmap(
            to_byte_stream_with_batch_parameters))
