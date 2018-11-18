from typing import (AnyStr,
                    IO)

from lz.textual import read_batch


def test_basic(stream: IO[AnyStr],
               stream_contents: AnyStr,
               batch_size: int,
               remaining_bytes_count: int) -> None:
    batch = read_batch(stream,
                       batch_size=batch_size,
                       remaining_bytes_count=remaining_bytes_count)

    assert batch in stream_contents
