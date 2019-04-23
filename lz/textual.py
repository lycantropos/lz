import codecs
from collections import defaultdict
from functools import partial
from typing import BinaryIO

from .hints import Map


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


# in bytes
code_units_sizes = defaultdict(lambda: 1,
                               {'utf_16': 2,
                                   'utf_16_be': 2,
                                   'utf_16_le': 2,
                                   'utf_32': 4,
                                   'utf_32_be': 4,
                                   'utf_32_le': 4})
