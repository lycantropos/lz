from typing import Tuple

from hypothesis import given

from lz.functional import compose
from lz.textual import (decoder,
                        encoder)
from tests.textual_tests import strategies
from tests.utils import (encoding_to_bom)
from tests.hints import ByteSequence


@given(strategies.byte_sequences_with_encodings)
def test_basic(byte_sequence_with_encoding: Tuple[ByteSequence, str]) -> None:
    byte_sequence, encoding = byte_sequence_with_encoding
    decode = decoder(encoding)

    result = decode(byte_sequence)

    assert isinstance(result, str)


@given(strategies.byte_sequences_with_encodings)
def test_round_trip(byte_sequence_with_encoding: Tuple[ByteSequence, str]
                    ) -> None:
    byte_sequence, encoding = byte_sequence_with_encoding
    make_round_trip = compose(encoder(encoding), decoder(encoding))

    result = make_round_trip(byte_sequence)

    is_unicode = encoding.startswith('utf')
    if is_unicode:
        bom = encoding_to_bom(encoding)

        assert isinstance(result, bytes)
        assert result in (byte_sequence, bom + byte_sequence)
    else:
        assert isinstance(result, bytes)
