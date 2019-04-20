from functools import partial
from typing import (Any,
                    IO,
                    Sequence)

from hypothesis import strategies

from lz.reversal import reverse
from tests.hints import (Strategy,
                         StreamWithReverseParameters)
from tests.strategies import (empty,
                              encodings,
                              min_finite_iterables_sizes,
                              objects,
                              to_byte_sequences,
                              to_byte_streams,
                              to_homogeneous_sequences,
                              to_separator,
                              to_strings,
                              to_text_streams)
from tests.utils import (to_stream_contents,
                         to_stream_size)

empty_sequences = empty.sequences
to_non_empty = partial(partial,
                       min_size=1)
non_empty_sequences = (encodings.flatmap(to_non_empty(to_byte_sequences))
                       | to_non_empty(to_homogeneous_sequences)(objects)
                       | encodings.flatmap(to_non_empty(to_strings)))


def to_sequences(min_iterables_size: int) -> Strategy[Sequence[Any]]:
    limit_min_size = partial(partial,
                             min_size=min_iterables_size)
    return (encodings.flatmap(limit_min_size(to_byte_sequences))
            | limit_min_size(to_homogeneous_sequences)(objects)
            | encodings.flatmap(limit_min_size(to_strings)))


sequences = min_finite_iterables_sizes.flatmap(to_sequences)


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


def is_object_irreversible(object_: Any) -> bool:
    return reverse.dispatch(type(object_)) is reverse.dispatch(object)


irreversible_objects = objects.filter(is_object_irreversible)
