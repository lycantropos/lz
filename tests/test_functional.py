from typing import Any

from lz.functional import (identity,
                           negate)
from lz.hints import Predicate


def test_identity(object_: Any) -> None:
    assert identity(object_) is object_


def test_negate(false_predicate: Predicate,
                true_predicate: Predicate) -> None:
    negated_false_predicate = negate(false_predicate)
    negated_true_predicate = negate(true_predicate)

    assert negated_false_predicate(None)
    assert not negated_true_predicate(None)
