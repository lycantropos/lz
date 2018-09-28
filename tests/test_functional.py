from typing import (Any,
                    Dict,
                    Tuple)

from lz.functional import (identity,
                           negate,
                           to_constant)
from lz.hints import Predicate


def test_identity(object_: Any) -> None:
    result = identity(object_)

    assert result is object_


def test_negate(false_predicate: Predicate,
                true_predicate: Predicate,
                positional_arguments: Tuple,
                keyword_arguments: Dict[str, Any]) -> None:
    non_false_predicate = negate(false_predicate)
    non_true_predicate = negate(true_predicate)

    non_false_predicate_result = non_false_predicate(*positional_arguments,
                                                     **keyword_arguments)
    non_true_predicate_result = non_true_predicate(*positional_arguments,
                                                   **keyword_arguments)

    assert isinstance(non_false_predicate_result, bool)
    assert isinstance(non_true_predicate_result, bool)
    assert non_false_predicate_result
    assert not non_true_predicate_result


def test_to_constant(object_: Any,
                     positional_arguments: Tuple,
                     keyword_arguments: Dict[str, Any]) -> None:
    constant = to_constant(object_)

    result = constant(*positional_arguments, **keyword_arguments)

    assert result is object_
