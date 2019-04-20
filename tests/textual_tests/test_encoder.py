from typing import Tuple

from hypothesis import given

from lz.functional import compose
from lz.textual import (decoder,
                        encoder)
from tests.textual_tests import strategies


@given(strategies.strings_with_encodings)
def test_basic(string_with_encoding: Tuple[str, str]) -> None:
    string, encoding = string_with_encoding
    encode = encoder(encoding)

    result = encode(string)

    assert isinstance(result, bytes)


@given(strategies.strings_with_encodings)
def test_round_trip(string_with_encoding: Tuple[str, str]) -> None:
    string, encoding = string_with_encoding
    make_round_trip = compose(decoder(encoding), encoder(encoding))

    result = make_round_trip(string)

    assert result == string
