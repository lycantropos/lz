import codecs
from functools import partial
from typing import (AnyStr,
                    BinaryIO,
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


def read_batch_from_end(byte_stream: BinaryIO,
                        *,
                        size: int,
                        end_position: int) -> bytes:
    """
    Reads batch from the end of given byte stream.
    """
    if end_position > size:
        offset = end_position - size
    else:
        offset = 0
        size = end_position
    byte_stream.seek(offset)
    return byte_stream.read(size)
