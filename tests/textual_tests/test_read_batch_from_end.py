import io
from typing import (AnyStr,
                    IO)

from lz.textual import read_batch_from_end


def test_basic(encoding: str,
               stream: IO[AnyStr],
               stream_contents: AnyStr,
               stream_batch_size: int,
               stream_batch_end_position: int) -> None:
    batch = read_batch_from_end(stream,
                                size=stream_batch_size,
                                end_position=stream_batch_end_position)

    is_byte_stream = isinstance(stream, io.BufferedIOBase)

    if is_byte_stream:
        assert batch in stream_contents
    else:
        assert batch.encode(encoding) in stream_contents.encode(encoding)
