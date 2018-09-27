from typing import Any

import pytest

from tests import strategies
from tests.utils import find


@pytest.fixture(scope='function')
def object_() -> Any:
    return find(strategies.objects)
