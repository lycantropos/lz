from typing import (Any,
                    Dict,
                    Tuple)

from lz.functional import (identity,
                           negate)
from lz.hints import Predicate


def test_identity(object_: Any) -> None:
    assert identity(object_) is object_


def test_negate(false_predicate: Predicate,
                true_predicate: Predicate,
                positional_arguments: Tuple,
                keyword_arguments: Dict[str, Any]) -> None:
    negated_false_predicate = negate(false_predicate)
    negated_true_predicate = negate(true_predicate)

    assert negated_false_predicate(*positional_arguments,
                                   **keyword_arguments)
    assert not negated_true_predicate(*positional_arguments,
                                      **keyword_arguments)
