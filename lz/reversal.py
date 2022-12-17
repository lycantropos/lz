import codecs as _codecs
import functools as _functools
import io as _io
import itertools as _itertools
import operator as _operator
import typing as _t
from collections import abc as _abc

from lz._core.arithmetical import ceil_division as _ceil_division
from lz._core.textual import (code_units_sizes as _code_units_sizes,
                              read_batch_from_end as _read_batch_from_end)

_T = _t.TypeVar('_T')


@_functools.singledispatch
def reverse(_value: _t.Any) -> _t.Any:
    """
    Returns reversed object.

    >>> list(reverse(range(10)))
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> import io
    >>> list(reverse(_io.BytesIO(b'Hello\\nWorld!')))
    [b'World!', b'Hello\\n']
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(_value)))


@reverse.register(_abc.Sequence)
def _(_value: _t.Sequence[_T]) -> _t.Sequence[_T]:
    """
    Returns reversed sequence.
    """
    return _value[::-1]


@reverse.register(_abc.Reversible)
def _(_value: _t.Reversible[_T]) -> _t.Iterable[_T]:
    """
    Returns reversed reversible iterable.
    """
    yield from reversed(_value)


@reverse.register(_io.TextIOWrapper)
def reverse_file_object(_value: _t.TextIO,
                        *,
                        batch_size: int = _io.DEFAULT_BUFFER_SIZE,
                        lines_separator: _t.Optional[str] = None,
                        keep_lines_separator: bool = True) -> _t.Iterable[str]:
    """
    Returns reversed file object.
    """
    encoding = _value.encoding
    code_unit_size = _code_units_sizes[encoding]
    bytes_lines_separator = (None
                             if lines_separator is None
                             else lines_separator.encode(encoding))
    yield from map(
            _functools.partial(_codecs.decode,
                               encoding=encoding),
            reverse_bytes_stream(_value.buffer,
                                 batch_size=batch_size,
                                 lines_separator=bytes_lines_separator,
                                 keep_lines_separator=keep_lines_separator,
                                 code_unit_size=code_unit_size)
    )


@reverse.register(_io.BufferedReader)
@reverse.register(_io.BytesIO)
def reverse_bytes_stream(_value: _t.BinaryIO,
                         *,
                         batch_size: int = _io.DEFAULT_BUFFER_SIZE,
                         lines_separator: _t.Optional[bytes] = None,
                         keep_lines_separator: bool = True,
                         code_unit_size: int = 1) -> _t.Iterable[bytes]:
    """
    Returns reversed byte stream.
    """
    lines_separators: _t.Union[bytes, _t.Tuple[bytes, ...]]
    lines_splitter: _t.Callable[[bytes], _t.List[bytes]]
    if lines_separator is None:
        lines_separators = (b'\r', b'\n', b'\r\n')
        lines_splitter = _operator.methodcaller(bytes.splitlines.__name__,
                                                keep_lines_separator)
    else:
        lines_separators = lines_separator
        _separator = lines_separator

        def lines_splitter(byte_sequence: bytes,
                           separator: bytes = _separator) -> _t.List[bytes]:
            result: _t.List[bytes] = []
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
    stream_size = _value.seek(0, _io.SEEK_END)
    batches_count = _ceil_division(stream_size, batch_size)
    remaining_bytes_indicator = _itertools.islice(
            _itertools.accumulate(
                    _itertools.chain([stream_size],
                                     _itertools.repeat(batch_size)),
                    _operator.sub
            ),
            batches_count
    )
    try:
        remaining_bytes_count = next(remaining_bytes_indicator)
    except StopIteration:
        return

    def read_batch(position: int) -> bytes:
        result = _read_batch_from_end(_value,
                                      size=batch_size,
                                      end_position=position)
        while result.startswith(lines_separators):
            try:
                position = next(remaining_bytes_indicator)
            except StopIteration:
                break
            result = (_read_batch_from_end(_value,
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
