from typing import Union

from lz.functional import compose
from lz.textual import (decoder,
                        encoder)


def test_basic(byte_sequence: Union[bytes, bytearray],
               encoding: str) -> None:
    decode = decoder(encoding)

    result = decode(byte_sequence)

    assert isinstance(result, str)


def test_inversion(byte_sequence: Union[bytes, bytearray],
                   encoding: str) -> None:
    composition = compose(encoder(encoding), decoder(encoding))

    result = composition(byte_sequence)

    assert isinstance(result, bytes)
    assert result == byte_sequence
