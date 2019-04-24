import codecs
import functools
import io
import itertools
import os
import sys
from collections import abc
from operator import (methodcaller,
                      sub)
from typing import (Any,
                    BinaryIO,
                    Iterable,
                    List,
                    Optional,
                    Sequence,
                    TextIO,
                    overload)

from .arithmetical import ceil_division
from .hints import (Domain,
                    Range)
from .textual import (code_units_sizes,
                      read_batch_from_end)


@overload
def reverse(object_: Sequence[Domain]) -> Sequence[Domain]:
    pass


if sys.version_info >= (3, 6):
    from typing import Reversible


    @overload
    def reverse(object_: Reversible[Domain]) -> Iterable[Domain]:
        pass


@overload
def reverse(object_: TextIO,
            *,
            batch_size: Optional[int] = ...,
            lines_separator: Optional[str] = ...,
            keep_lines_separator: bool = ...) -> Iterable[str]:
    pass


@overload
def reverse(object_: BinaryIO,
            *,
            batch_size: Optional[int] = ...,
            lines_separator: Optional[bytes] = ...,
            keep_lines_separator: bool = ...,
            code_unit_size: int = ...) -> Iterable[bytes]:
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
    code_unit_size = code_units_sizes[encoding]
    if batch_size is not None:
        batch_size = ceil_division(batch_size, code_unit_size) * code_unit_size
    yield from map(functools.partial(codecs.decode,
                                     encoding=encoding),
                   reverse(object_.buffer,
                           batch_size=batch_size,
                           lines_separator=lines_separator,
                           keep_lines_separator=keep_lines_separator,
                           code_unit_size=code_unit_size))


@reverse.register(io.BufferedReader)
@reverse.register(io.BytesIO)
def reverse_binary_stream(object_: BinaryIO,
                          *,
                          batch_size: Optional[int] = None,
                          lines_separator: Optional[bytes] = None,
                          keep_lines_separator: bool = True,
                          code_unit_size: int = 1
                          ) -> Iterable[bytes]:
    if lines_separator is None:
        lines_separator = (b'\r', b'\n', b'\r\n')
        lines_splitter = methodcaller(bytes.splitlines.__name__,
                                      keep_lines_separator)
    else:
        def lines_splitter(byte_sequence: bytes) -> List[bytes]:
            result = []
            part = bytearray()
            offset = 0
            add_part = result.append
            while offset < len(byte_sequence):
                if (byte_sequence[offset:offset + len(lines_separator)]
                        != lines_separator):
                    part += byte_sequence[offset:offset + code_unit_size]
                    offset += code_unit_size
                else:
                    add_part(part + keep_lines_separator * lines_separator)
                    part.clear()
                    offset += len(lines_separator)
            add_part(part)
            return result
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

    def read_batch(position: int) -> bytes:
        result = read_batch_from_end(object_,
                                     size=batch_size,
                                     end_position=position)
        while result.startswith(lines_separator):
            try:
                position = next(remaining_bytes_indicator)
            except StopIteration:
                break
            result = (read_batch_from_end(object_,
                                          size=batch_size,
                                          end_position=position)
                      + result)
        return result

    batch = read_batch(remaining_bytes_count)
    segment, *lines = lines_splitter(batch)
    yield from reverse(lines)
    for remaining_bytes_count in remaining_bytes_indicator:
        batch = read_batch(remaining_bytes_count)
        lines = lines_splitter(batch)
        if batch.endswith(lines_separator):
            yield segment
        else:
            lines[-1] += segment
        segment, *lines = lines
        yield from reverse(lines)
    yield segment
