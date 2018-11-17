from typing import Union

from lz.functional import compose
from lz.textual import (decoder,
                        encoder)


def test_basic(string: str,
               encoding: str) -> None:
    encode = encoder(encoding)

    result = encode(string)

    assert isinstance(result, bytes)


def test_inversion(string: str,
                   encoding: str) -> None:
    composition = compose(decoder(encoding), encoder(encoding))

    result = composition(string)

    assert isinstance(result, str)
    assert result == string
