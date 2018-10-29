from lz.hints import (Domain,
                      Predicate)
from lz.logical import disjoin


def test_idempotency(predicate: Predicate,
                     predicate_argument: Domain) -> None:
    self_disjunction = disjoin(predicate)

    result = self_disjunction(predicate_argument)

    assert result is predicate(predicate_argument)


def test_absorbing_element(predicate: Predicate,
                           true_predicate: Predicate,
                           predicate_argument: Domain) -> None:
    left_disjunction = disjoin(predicate, true_predicate)
    right_disjunction = disjoin(true_predicate, predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result is true_predicate(predicate_argument)


def test_neutral_element(predicate: Predicate,
                         false_predicate: Predicate,
                         predicate_argument: Domain) -> None:
    left_disjunction = disjoin(predicate, false_predicate)
    right_disjunction = disjoin(false_predicate, predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result is predicate(predicate_argument)


def test_commutativity(left_predicate: Predicate,
                       right_predicate: Predicate,
                       predicate_argument: Domain) -> None:
    left_disjunction = disjoin(left_predicate, right_predicate)
    right_disjunction = disjoin(right_predicate, left_predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result


def test_associativity(left_predicate: Predicate,
                       mid_predicate: Predicate,
                       right_predicate: Predicate,
                       predicate_argument: Domain) -> None:
    left_disjunction = disjoin(left_predicate, right_predicate)
    right_disjunction = disjoin(right_predicate, left_predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result
