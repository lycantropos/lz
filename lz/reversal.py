import codecs
import functools
import io
import itertools
import os
from collections import abc
from operator import (methodcaller,
                      sub)
from typing import (Any,
                    BinaryIO,
                    Callable, Iterable,
                    List,
                    Optional,
                    Reversible,
                    Sequence,
                    TextIO, Tuple, Union)

from .arithmetical import ceil_division
from .hints import Domain
from .textual import (code_units_sizes,
                      read_batch_from_end)


@functools.singledispatch
def reverse(_value: Any) -> Any:
    """
    Returns reversed object.

    >>> list(reverse(range(10)))
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> import io
    >>> list(reverse(io.BytesIO(b'Hello\\nWorld!')))
    [b'World!', b'Hello\\n']
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(_value)))


@reverse.register(abc.Sequence)
def _(_value: Sequence[Domain]) -> Sequence[Domain]:
    """
    Returns reversed sequence.
    """
    return _value[::-1]


@reverse.register(abc.Reversible)
def _(_value: Reversible[Domain]) -> Iterable[Domain]:
    """
    Returns reversed reversible iterable.
    """
    yield from reversed(_value)


@reverse.register(io.TextIOWrapper)
def reverse_file_object(_value: TextIO,
                        *,
                        batch_size: int = io.DEFAULT_BUFFER_SIZE,
                        lines_separator: Optional[str] = None,
                        keep_lines_separator: bool = True) -> Iterable[str]:
    """
    Returns reversed file object.
    """
    encoding = _value.encoding
    code_unit_size = code_units_sizes[encoding]
    bytes_lines_separator = (None
                             if lines_separator is None
                             else lines_separator.encode(encoding))
    yield from map(
            functools.partial(codecs.decode,
                              encoding=encoding),
            reverse_bytes_stream(_value.buffer,
                                 batch_size=batch_size,
                                 lines_separator=bytes_lines_separator,
                                 keep_lines_separator=keep_lines_separator,
                                 code_unit_size=code_unit_size)
    )


@reverse.register(io.BufferedReader)
@reverse.register(io.BytesIO)
def reverse_bytes_stream(_value: BinaryIO,
                         *,
                         batch_size: int = io.DEFAULT_BUFFER_SIZE,
                         lines_separator: Optional[bytes] = None,
                         keep_lines_separator: bool = True,
                         code_unit_size: int = 1) -> Iterable[bytes]:
    """
    Returns reversed byte stream.
    """
    lines_separators: Union[bytes, Tuple[bytes, ...]]
    lines_splitter: Callable[[bytes], List[bytes]]
    if lines_separator is None:
        lines_separators = (b'\r', b'\n', b'\r\n')
        lines_splitter = methodcaller(bytes.splitlines.__name__,
                                      keep_lines_separator)
    else:
        lines_separators = lines_separator
        _separator = lines_separator

        def lines_splitter(byte_sequence: bytes,
                           separator: bytes = _separator) -> List[bytes]:
            result: List[bytes] = []
            part = bytearray()
            offset = 0
            add_part = result.append
            while offset < len(byte_sequence):
                if (byte_sequence[offset:offset + len(separator)]
                        != separator):
                    part += byte_sequence[offset:offset + code_unit_size]
                    offset += code_unit_size
                else:
                    add_part(part + keep_lines_separator * separator)
                    part.clear()
                    offset += len(separator)
            add_part(part)
            return result
    stream_size = _value.seek(0, os.SEEK_END)
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
        result = read_batch_from_end(_value,
                                     size=batch_size,
                                     end_position=position)
        while result.startswith(lines_separators):
            try:
                position = next(remaining_bytes_indicator)
            except StopIteration:
                break
            result = (read_batch_from_end(_value,
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
        if batch.endswith(lines_separators):
            yield segment
        else:
            lines[-1] += segment
        segment, *lines = lines
        yield from reverse(lines)
    yield segment
