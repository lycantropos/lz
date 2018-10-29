from typing import (Any,
                    Dict,
                    Tuple)

from lz.hints import Predicate
from lz.logical import negate


def test_basic(false_predicate: Predicate,
               true_predicate: Predicate,
               positional_arguments: Tuple,
               keyword_arguments: Dict[str, Any]) -> None:
    negated_false_predicate = negate(false_predicate)
    negated_true_predicate = negate(true_predicate)

    negated_false_predicate_result = negated_false_predicate(
            *positional_arguments,
            **keyword_arguments)
    negated_true_predicate_result = negated_true_predicate(
            *positional_arguments,
            **keyword_arguments)

    assert isinstance(negated_false_predicate_result, bool)
    assert isinstance(negated_true_predicate_result, bool)
    assert negated_false_predicate_result
    assert not negated_true_predicate_result


def test_involution(false_predicate: Predicate,
                    true_predicate: Predicate,
                    positional_arguments: Tuple,
                    keyword_arguments: Dict[str, Any]) -> None:
    double_negated_false_predicate = negate(negate(false_predicate))
    double_negated_true_predicate = negate(negate(true_predicate))

    double_negated_false_predicate_result = double_negated_false_predicate(
            *positional_arguments,
            **keyword_arguments)
    double_negated_true_predicate_result = double_negated_true_predicate(
            *positional_arguments,
            **keyword_arguments)

    assert isinstance(double_negated_false_predicate_result, bool)
    assert isinstance(double_negated_true_predicate_result, bool)
    assert not double_negated_false_predicate_result
    assert double_negated_true_predicate_result
