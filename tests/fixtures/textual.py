import os
import random
from typing import (AnyStr,
                    BinaryIO,
                    IO,
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
def byte_stream_batch_end_position(stream_size: int) -> int:
    return find(strategies.to_integers(0, stream_size))


@pytest.fixture(scope='function')
def byte_stream_batch_size(byte_stream_size: int) -> int:
    max_batch_size = max(byte_stream_size, 1)
    return find(strategies.to_integers(1, max_batch_size))


@pytest.fixture(scope='function')
def byte_stream_contents(byte_stream: BinaryIO) -> bytes:
    return to_stream_contents(byte_stream)


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
def stream(encoding: str) -> IO[AnyStr]:
    return find(strategies.to_any_streams(encoding))


@pytest.fixture(scope='function')
def stream_batch_size(stream_size: int) -> int:
    max_batch_size = max(stream_size, 1)
    return find(strategies.to_integers(1, max_batch_size))


@pytest.fixture(scope='function')
def stream_contents(stream: IO[AnyStr]) -> AnyStr:
    return to_stream_contents(stream)


@pytest.fixture(scope='function')
def stream_lines_separator(stream_contents: AnyStr) -> AnyStr:
    return to_separator(stream_contents)


@pytest.fixture(scope='function')
def stream_size(stream: IO[AnyStr]) -> int:
    return to_stream_size(stream)


@pytest.fixture(scope='function')
def string(byte_sequence: Union[bytearray, bytes],
           encoding: str) -> str:
    return byte_sequence.decode(encoding)


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
