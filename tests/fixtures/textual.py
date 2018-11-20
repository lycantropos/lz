import os
import random
from typing import (AnyStr,
                    BinaryIO,
                    IO,
                    TextIO,
                    Union)

import pytest

from tests import strategies
from tests.utils import find


@pytest.fixture(scope='function')
def any_string() -> AnyStr:
    return find(strategies.any_strings)


@pytest.fixture(scope='function')
def any_separator(any_string: AnyStr) -> AnyStr:
    return to_separator(any_string)


@pytest.fixture(scope='function')
def byte_sequence(encoding: str) -> Union[bytearray, bytes]:
    return find(strategies.to_byte_sequences(encoding))


@pytest.fixture(scope='function')
def byte_stream(encoding: str) -> BinaryIO:
    return find(strategies.to_byte_streams(encoding))


@pytest.fixture(scope='function')
def byte_stream_batch_end_position(byte_stream_size: int) -> int:
    return find(strategies.to_integers(0, byte_stream_size))


@pytest.fixture(scope='function')
def byte_stream_batch_size(byte_stream_size: int) -> int:
    max_batch_size = max(byte_stream_size, 1)
    return find(strategies.to_integers(1, max_batch_size))


@pytest.fixture(scope='function')
def byte_stream_contents(byte_stream: BinaryIO) -> bytes:
    return to_stream_contents(byte_stream)


@pytest.fixture(scope='function')
def byte_stream_lines_separator(encoding: str) -> bytes:
    return find(strategies.to_byte_sequences(encoding,
                                             min_size=1))


@pytest.fixture(scope='function')
def byte_stream_size(byte_stream: BinaryIO) -> int:
    return to_stream_size(byte_stream)


@pytest.fixture(scope='function')
def encoding() -> str:
    return find(strategies.encodings)


@pytest.fixture(scope='function')
def keep_separator() -> bool:
    return find(strategies.booleans)


@pytest.fixture(scope='function')
def string(byte_sequence: Union[bytearray, bytes],
           encoding: str) -> str:
    return byte_sequence.decode(encoding)


@pytest.fixture(scope='function')
def text_stream(encoding: str) -> TextIO:
    return find(strategies.to_text_streams(encoding))


@pytest.fixture(scope='function')
def text_stream_batch_size(text_stream_size: int) -> int:
    max_batch_size = max(text_stream_size, 1)
    return find(strategies.to_integers(1, max_batch_size))


@pytest.fixture(scope='function')
def text_stream_raw_contents(text_stream: TextIO) -> bytes:
    return to_stream_contents(text_stream.buffer)


@pytest.fixture(scope='function')
def text_stream_lines_separator(encoding: str) -> str:
    return (find(strategies.to_byte_sequences(encoding,
                                              min_size=1))
            .decode(encoding))


@pytest.fixture(scope='function')
def text_stream_size(text_stream: TextIO) -> int:
    return to_stream_size(text_stream)


def to_separator(any_string: AnyStr) -> AnyStr:
    if not any_string:
        result = os.sep
        if not isinstance(any_string, str):
            return result.encode()
        return result
    string_length = len(any_string)
    start = random.randint(0, string_length - 1)
    stop = random.randint(start + 1, string_length)
    return any_string[start:stop]


def to_stream_contents(stream: IO[AnyStr]) -> AnyStr:
    result = stream.read()
    stream.seek(0)
    return result


def to_stream_size(stream: IO[AnyStr]) -> int:
    result = stream.seek(0, os.SEEK_END)
    stream.seek(0)
    return result
