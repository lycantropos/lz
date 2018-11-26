from typing import Union

from lz.functional import compose
from lz.textual import (decoder,
                        encoder)
from tests.utils import encoding_to_bom


def test_basic(byte_sequence: Union[bytearray, bytes],
               encoding: str) -> None:
    decode = decoder(encoding)

    result = decode(byte_sequence)

    assert isinstance(result, str)


def test_round_trip(byte_sequence: Union[bytearray, bytes],
                    encoding: str) -> None:
    make_round_trip = compose(encoder(encoding), decoder(encoding))

    result = make_round_trip(byte_sequence)

    is_unicode = encoding.startswith('utf')
    if is_unicode:
        bom = encoding_to_bom(encoding)

        assert isinstance(result, bytes)
        assert result in (byte_sequence, bom + byte_sequence)
    else:
        assert isinstance(result, bytes)
