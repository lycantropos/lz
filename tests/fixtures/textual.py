import os
import random
from typing import AnyStr

import pytest

from tests import strategies
from tests.utils import find


@pytest.fixture(scope='function')
def any_string() -> AnyStr:
    return find(strategies.to_any_strings())


@pytest.fixture(scope='function')
def any_separator(any_string: AnyStr) -> AnyStr:
    if not any_separator:
        return type(any_string)(os.sep)
    string_length = len(any_string)
    start = random.randint(0, string_length - 1)
    stop = random.randint(start + 1, string_length)
    return any_string[start:stop]


@pytest.fixture(scope='function')
def keep_separator() -> bool:
    return find(strategies.booleans)
