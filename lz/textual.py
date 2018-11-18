import codecs
from functools import partial
from typing import (AnyStr,
                    IO,
                    List)

from .hints import Map


def split(string: AnyStr,
          *,
          separator: AnyStr,
          keep_separator: bool) -> List[AnyStr]:
    """
    Splits given string by given separator.
    """
    parts = string.split(separator)
    if keep_separator:
        *parts, last_part = parts
        parts = [part + separator for part in parts]
        if last_part:
            return parts + [last_part]
    return parts


def decoder(encoding: str) -> Map[bytes, str]:
    """
    Returns function that decodes byte sequence
    with codec registered for given encoding.
    """
    return partial(codecs.decode,
                   encoding=encoding)


def encoder(encoding: str) -> Map[str, bytes]:
    """
    Returns function that encodes string
    with codec registered for given encoding.
    """
    return partial(codecs.encode,
                   encoding=encoding)


def read_batch(stream: IO[AnyStr],
               *,
               batch_size: int,
               remaining_bytes_count: int) -> AnyStr:
    """
    Reads batch from given stream.
    """
    if remaining_bytes_count > batch_size:
        offset = remaining_bytes_count - batch_size
    else:
        offset = 0
        batch_size = remaining_bytes_count
    stream.seek(offset)
    return stream.read(batch_size)
