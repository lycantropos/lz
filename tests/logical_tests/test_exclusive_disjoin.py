from lz.hints import (Domain,
                      Predicate)
from lz.logical import exclusive_disjoin


def test_idempotency(predicate: Predicate,
                     predicate_argument: Domain) -> None:
    self_disjunction = exclusive_disjoin(predicate)

    result = self_disjunction(predicate_argument)

    assert result is predicate(predicate_argument)


def test_neutral_element(predicate: Predicate,
                         false_predicate: Predicate,
                         predicate_argument: Domain) -> None:
    left_disjunction = exclusive_disjoin(predicate, false_predicate)
    right_disjunction = exclusive_disjoin(false_predicate, predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result is predicate(predicate_argument)


def test_commutativity(left_predicate: Predicate,
                       right_predicate: Predicate,
                       predicate_argument: Domain) -> None:
    left_disjunction = exclusive_disjoin(left_predicate, right_predicate)
    right_disjunction = exclusive_disjoin(right_predicate, left_predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result


def test_associativity(left_predicate: Predicate,
                       mid_predicate: Predicate,
                       right_predicate: Predicate,
                       predicate_argument: Domain) -> None:
    left_disjunction = exclusive_disjoin(left_predicate, right_predicate)
    right_disjunction = exclusive_disjoin(right_predicate, left_predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result
