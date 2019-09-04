import os
from functools import partial
from typing import (Any,
                    AnyStr,
                    IO,
                    Sequence,
                    Tuple)

from hypothesis import strategies

from lz.functional import pack
from tests.hints import (Strategy,
                         StreamWithReverseParameters)
from tests.strategies import (empty,
                              encodings,
                              scalars,
                              to_any_strings,
                              to_byte_streams,
                              to_homogeneous_sequences,
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


def to_separator(any_string: AnyStr) -> Strategy[AnyStr]:
    if not any_string:
        result = os.linesep
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


byte_streams_with_reverse_parameters = (
    encodings.flatmap(to_byte_streams).flatmap(
            to_stream_with_reverse_parameters))
text_streams_with_reverse_parameters = (
    encodings.flatmap(to_text_streams).flatmap(
            to_stream_with_reverse_parameters))
