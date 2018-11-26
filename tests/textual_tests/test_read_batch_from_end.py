from typing import BinaryIO

from lz.textual import read_batch_from_end


def test_basic(byte_stream: BinaryIO,
               byte_stream_contents: bytes,
               byte_stream_batch_size: int,
               byte_stream_batch_end_position: int) -> None:
    batch = read_batch_from_end(byte_stream,
                                size=byte_stream_batch_size,
                                end_position=byte_stream_batch_end_position)

    assert batch in byte_stream_contents
