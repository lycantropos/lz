from functools import partial
from types import (FunctionType,
                   MethodType)
from typing import Sequence

import pytest
from paradigm.hints import (MethodDescriptorType,
                            WrapperDescriptorType)

from tests import strategies
from tests.utils import (find,
                         is_pickleable)


@pytest.fixture(scope='function')
def class_() -> type:
    return find(strategies.classes)


@pytest.fixture(scope='function')
def other_class() -> type:
    return find(strategies.classes)


@pytest.fixture(scope='function')
def another_class() -> type:
    return find(strategies.classes)


@pytest.fixture(scope='function')
def classes() -> Sequence[type]:
    return find(strategies.to_homogeneous_sequences(strategies.classes))


@pytest.fixture(scope='function')
def pickleable_classes() -> Sequence[type]:
    return find(strategies.to_homogeneous_sequences(strategies.classes
                                                    .filter(is_pickleable)))
