from functools import partial
from typing import (Any,
                    IO,
                    Sequence)

from hypothesis import strategies

from tests.hints import (Strategy,
                         StreamWithReverseParameters)
from tests.strategies import (empty,
                              encodings,
                              scalars,
                              to_any_strings,
                              to_byte_streams,
                              to_homogeneous_sequences,
                              to_separator,
                              to_text_streams)
from tests.utils import (to_stream_contents,
                         to_stream_size)

empty_sequences = empty.sequences


def to_sequences(min_size: int) -> Strategy[Sequence[Any]]:
    limit_min_size = partial(partial,
                             min_size=min_size)
    return (encodings.flatmap(limit_min_size(to_any_strings))
            | limit_min_size(to_homogeneous_sequences)(scalars))


non_empty_sequences = to_sequences(1)
sequences = to_sequences(0)


def to_stream_with_reverse_parameters(
        stream: IO) -> Strategy[StreamWithReverseParameters]:
    contents = to_stream_contents(stream)
    stream_size = to_stream_size(stream)
    batches_sizes = strategies.integers(1, max(stream_size, 1))
    return strategies.tuples(strategies.just(stream),
                             strategies.just(contents),
                             strategies.tuples(batches_sizes,
                                               to_separator(contents),
                                               strategies.booleans()))


byte_streams_with_reverse_parameters = (
    encodings.flatmap(to_byte_streams).flatmap(
            to_stream_with_reverse_parameters))
text_streams_with_reverse_parameters = (
    encodings.flatmap(to_text_streams).flatmap(
            to_stream_with_reverse_parameters))
