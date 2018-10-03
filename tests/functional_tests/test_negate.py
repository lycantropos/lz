from typing import (Any,
                    Dict,
                    Tuple)

from lz.functional import negate
from lz.hints import Predicate


def test_basic(false_predicate: Predicate,
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


def test_involution(false_predicate: Predicate,
                    true_predicate: Predicate,
                    positional_arguments: Tuple,
                    keyword_arguments: Dict[str, Any]) -> None:
    non_non_false_predicate = negate(negate(false_predicate))
    non_non_true_predicate = negate(negate(true_predicate))

    non_non_false_predicate_result = non_non_false_predicate(
            *positional_arguments,
            **keyword_arguments)
    non_non_true_predicate_result = non_non_true_predicate(
            *positional_arguments,
            **keyword_arguments)

    assert isinstance(non_non_false_predicate_result, bool)
    assert isinstance(non_non_true_predicate_result, bool)
    assert not non_non_false_predicate_result
    assert non_non_true_predicate_result
