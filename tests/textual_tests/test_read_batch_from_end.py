from typing import (AnyStr,
                    IO)

from lz.textual import read_batch_from_end


def test_basic(stream: IO[AnyStr],
               stream_contents: AnyStr,
               stream_batch_size: int,
               stream_batch_end_position: int) -> None:
    batch = read_batch_from_end(stream,
                                size=stream_batch_size,
                                end_position=stream_batch_end_position)

    assert batch in stream_contents
