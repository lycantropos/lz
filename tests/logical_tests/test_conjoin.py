from lz.hints import (Domain,
                      Predicate)
from lz.logical import conjoin


def test_idempotency(predicate: Predicate,
                     predicate_argument: Domain) -> None:
    self_conjunction = conjoin(predicate)

    result = self_conjunction(predicate_argument)

    assert result is predicate(predicate_argument)


def test_absorbing_element(predicate: Predicate,
                           false_predicate: Predicate,
                           predicate_argument: Domain) -> None:
    left_conjunction = conjoin(predicate, false_predicate)
    right_conjunction = conjoin(false_predicate, predicate)

    left_result = left_conjunction(predicate_argument)
    right_result = right_conjunction(predicate_argument)

    assert left_result is right_result is false_predicate(predicate_argument)


def test_neutral_element(predicate: Predicate,
                         true_predicate: Predicate,
                         predicate_argument: Domain) -> None:
    left_conjunction = conjoin(predicate, true_predicate)
    right_conjunction = conjoin(true_predicate, predicate)

    left_result = left_conjunction(predicate_argument)
    right_result = right_conjunction(predicate_argument)

    assert left_result is right_result is predicate(predicate_argument)


def test_commutativity(left_predicate: Predicate,
                       right_predicate: Predicate,
                       predicate_argument: Domain) -> None:
    left_conjunction = conjoin(left_predicate, right_predicate)
    right_conjunction = conjoin(right_predicate, left_predicate)

    left_result = left_conjunction(predicate_argument)
    right_result = right_conjunction(predicate_argument)

    assert left_result is right_result


def test_associativity(left_predicate: Predicate,
                       mid_predicate: Predicate,
                       right_predicate: Predicate,
                       predicate_argument: Domain) -> None:
    left_conjunction = conjoin(conjoin(left_predicate, right_predicate),
                               mid_predicate)
    right_conjunction = conjoin(left_predicate,
                                conjoin(mid_predicate, right_predicate))

    left_result = left_conjunction(predicate_argument)
    right_result = right_conjunction(predicate_argument)

    assert left_result is right_result
