import codecs
from collections import defaultdict
from typing import Union

from lz.functional import compose
from lz.textual import (decoder,
                        encoder)


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
        bom = unicode_encoding_to_bom(encoding)
        assert result in (byte_sequence, bom + byte_sequence)
    else:
        assert not result or set(result) & set(byte_sequence)


unicode_encoding_to_bom = (defaultdict(bytes,
                                       {'utf_8_sig': codecs.BOM_UTF8,
                                        'utf_16': codecs.BOM_UTF16,
                                        'utf_16_be': codecs.BOM_UTF16_BE,
                                        'utf_16_le': codecs.BOM_UTF16_LE,
                                        'utf_32': codecs.BOM_UTF32,
                                        'utf_32_be': codecs.BOM_UTF32_BE,
                                        'utf_32_le': codecs.BOM_UTF32_LE})
                           .__getitem__)
