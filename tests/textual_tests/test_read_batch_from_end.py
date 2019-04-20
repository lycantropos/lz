from hypothesis import given

from lz.textual import read_batch_from_end
from tests.hints import ByteStreamWithBatchParameters
from tests.textual_tests import strategies


@given(strategies.byte_streams_with_batch_parameters)
def test_basic(stream_with_batch_parameters: ByteStreamWithBatchParameters
               ) -> None:
    (stream,
     contents,
     (batch_size, batch_end_position)) = stream_with_batch_parameters
    batch = read_batch_from_end(stream,
                                size=batch_size,
                                end_position=batch_end_position)

    assert batch in contents
