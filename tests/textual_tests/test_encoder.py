from lz.functional import compose
from lz.textual import (decoder,
                        encoder)


def test_basic(string: str,
               encoding: str) -> None:
    encode = encoder(encoding)

    result = encode(string)

    assert isinstance(result, bytes)


def test_round_trip(string: str,
                    encoding: str) -> None:
    make_round_trip = compose(decoder(encoding), encoder(encoding))

    result = make_round_trip(string)

    assert result == string
