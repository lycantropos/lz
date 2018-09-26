import pytest

from lz.hints import Predicate
from tests import strategies
from tests.utils import example


@pytest.fixture(scope='session')
def false_predicate() -> Predicate:
    return example(strategies.false_predicates)


@pytest.fixture(scope='session')
def predicate() -> Predicate:
    return example(strategies.predicates)


@pytest.fixture(scope='session')
def true_predicate() -> Predicate:
    return example(strategies.true_predicates)
