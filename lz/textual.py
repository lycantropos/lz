from collections import defaultdict
from typing import BinaryIO


def read_batch_from_end(byte_stream: BinaryIO,
                        *,
                        size: int,
                        end_position: int) -> bytes:
    """
    Reads batch from the end of given byte stream.

    >>> import io
    >>> byte_stream = io.BytesIO(b'Hello\\nWorld!')
    >>> read_batch_from_end(byte_stream, size=4, end_position=5)
    b'ello'
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
