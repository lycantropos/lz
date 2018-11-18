import os
import random
from typing import (AnyStr,
                    IO,
                    Union)

import pytest

from tests import strategies
from tests.utils import find


@pytest.fixture(scope='function')
def any_string() -> AnyStr:
    return find(strategies.to_any_strings())


@pytest.fixture(scope='function')
def any_separator(any_string: AnyStr) -> AnyStr:
    if not any_string:
        result = os.sep
        if not isinstance(any_string, str):
            return result.encode()
        return result
    string_length = len(any_string)
    start = random.randint(0, string_length - 1)
    stop = random.randint(start + 1, string_length)
    return any_string[start:stop]


@pytest.fixture(scope='function')
def batch_size(stream_size: int) -> int:
    return find(strategies.to_integers(0, stream_size))


@pytest.fixture(scope='function')
def byte_sequence(encoding: str) -> Union[bytearray, bytes]:
    result = find(strategies.to_byte_sequences())
    return type(result)(result.decode(encoding, 'ignore')
                        .encode(encoding))


@pytest.fixture(scope='function')
def encoding() -> str:
    return find(strategies.supported_encodings)


@pytest.fixture(scope='function')
def keep_separator() -> bool:
    return find(strategies.booleans)


@pytest.fixture(scope='function')
def remaining_bytes_count(stream_size: int) -> int:
    return find(strategies.to_integers(0, stream_size))


@pytest.fixture(scope='function')
def stream() -> IO[AnyStr]:
    return find(strategies.to_any_streams())


@pytest.fixture(scope='function')
def stream_contents(stream: IO[AnyStr]) -> AnyStr:
    result = stream.read()
    stream.seek(0)
    return result


@pytest.fixture(scope='function')
def stream_size(stream: IO[AnyStr]) -> int:
    result = stream.seek(0, os.SEEK_END)
    stream.seek(0)
    return result


@pytest.fixture(scope='function')
def string(byte_sequence: Union[bytearray, bytes],
           encoding: str) -> str:
    return byte_sequence.decode(encoding)
