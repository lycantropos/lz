import functools
import io
import itertools
import os
import sys
from collections import abc
from operator import (methodcaller,
                      sub)
from typing import (Any,
                    AnyStr,
                    BinaryIO,
                    IO,
                    Iterable,
                    Optional,
                    Sequence,
                    TextIO,
                    overload)

from .arithmetical import ceil_division
from .hints import (Domain,
                    Range)
from .textual import (decoder,
                      read_batch_from_end,
                      rsplit)


@overload
def reverse(object_: Sequence[Domain]) -> Sequence[Domain]:
    pass


if sys.version_info >= (3, 6):
    from typing import Reversible


    @overload
    def reverse(object_: Reversible[Domain]) -> Iterable[Domain]:
        pass


@overload
def reverse(object_: IO[AnyStr],
            *,
            batch_size: Optional[int] = ...,
            lines_separator: Optional[AnyStr] = ...,
            keep_lines_separator: bool = ...) -> Iterable[AnyStr]:
    pass


@overload
def reverse(object_: Domain) -> Range:
    pass


@functools.singledispatch
def reverse(object_: Domain, **_: Any) -> Range:
    """
    Returns reversed object.
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


@reverse.register(abc.Sequence)
def reverse_sequence(object_: Sequence[Domain]) -> Sequence[Domain]:
    return object_[::-1]


if sys.version_info >= (3, 6):
    from typing import Reversible


    @reverse.register(abc.Reversible)
    def reverse_reversible(object_: Reversible[Domain]) -> Iterable[Domain]:
        yield from reversed(object_)


@reverse.register(io.TextIOWrapper)
def reverse_file(object_: TextIO,
                 *,
                 batch_size: Optional[int] = None,
                 lines_separator: Optional[str] = None,
                 keep_lines_separator: bool = True) -> Iterable[str]:
    encoding = object_.encoding
    if lines_separator is not None:
        lines_separator = lines_separator.encode(encoding)
    yield from map(decoder(encoding),
                   reverse(object_.buffer,
                           batch_size=batch_size,
                           lines_separator=lines_separator,
                           keep_lines_separator=keep_lines_separator))


@reverse.register(io.BufferedReader)
@reverse.register(io.BytesIO)
def reverse_binary_stream(object_: BinaryIO,
                          *,
                          batch_size: Optional[int] = None,
                          lines_separator: Optional[bytes] = None,
                          keep_lines_separator: bool = True
                          ) -> Iterable[bytes]:
    if lines_separator is None:
        lines_separator = (b'\r', b'\n', b'\r\n')
        lines_splitter = methodcaller(str.splitlines.__name__,
                                      keep_lines_separator)
    else:
        lines_splitter = functools.partial(rsplit,
                                           separator=lines_separator,
                                           keep_separator=keep_lines_separator)
    stream_size = object_.seek(0, os.SEEK_END)
    if batch_size is None:
        batch_size = stream_size or 1
    batches_count = ceil_division(stream_size, batch_size)
    remaining_bytes_indicator = itertools.islice(
            itertools.accumulate(itertools.chain([stream_size],
                                                 itertools.repeat(batch_size)),
                                 sub),
            batches_count)
    try:
        remaining_bytes_count = next(remaining_bytes_indicator)
    except StopIteration:
        return
    batch = read_batch_from_end(object_,
                                size=batch_size,
                                end_position=remaining_bytes_count)
    segment, *lines = lines_splitter(batch)
    yield from reverse(lines)
    for remaining_bytes_count in remaining_bytes_indicator:
        batch = read_batch_from_end(object_,
                                    size=batch_size,
                                    end_position=remaining_bytes_count)
        lines = lines_splitter(batch)
        if batch.endswith(lines_separator):
            yield segment
        else:
            lines[-1] += segment
        segment, *lines = lines
        yield from reverse(lines)
    yield segment
