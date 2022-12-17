from typing import Callable

from hypothesis import given

from lz.hints import Domain
from lz.logical import disjoin
from tests import strategies


@given(strategies.predicates, strategies.predicates_arguments)
def test_idempotency(predicate: Callable[[Domain], bool],
                     predicate_argument: Domain) -> None:
    self_disjunction = disjoin(predicate)

    result = self_disjunction(predicate_argument)

    assert result is predicate(predicate_argument)


@given(strategies.predicates, strategies.true_predicates,
       strategies.predicates_arguments)
def test_absorbing_element(predicate: Callable[[Domain], bool],
                           true_predicate: Callable[[Domain], bool],
                           predicate_argument: Domain) -> None:
    left_disjunction = disjoin(predicate, true_predicate)
    right_disjunction = disjoin(true_predicate, predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result is true_predicate(predicate_argument)


@given(strategies.predicates, strategies.false_predicates,
       strategies.predicates_arguments)
def test_neutral_element(predicate: Callable[[Domain], bool],
                         false_predicate: Callable[[Domain], bool],
                         predicate_argument: Domain) -> None:
    left_disjunction = disjoin(predicate, false_predicate)
    right_disjunction = disjoin(false_predicate, predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result is predicate(predicate_argument)


@given(strategies.predicates, strategies.predicates,
       strategies.predicates_arguments)
def test_commutativity(left_predicate: Callable[[Domain], bool],
                       right_predicate: Callable[[Domain], bool],
                       predicate_argument: Domain) -> None:
    left_disjunction = disjoin(left_predicate, right_predicate)
    right_disjunction = disjoin(right_predicate, left_predicate)

    left_result = left_disjunction(predicate_argument)
    right_result = right_disjunction(predicate_argument)

    assert left_result is right_result


@given(strategies.predicates, strategies.predicates, strategies.predicates,
       strategies.predicates_arguments)
def test_associativity(left_predicate: Callable[[Domain], bool],
                       mid_predicate: Callable[[Domain], bool],
                       right_predicate: Callable[[Domain], bool],
                       predicate_argument: Domain) -> None:
    first_disjunction = disjoin(disjoin(left_predicate, mid_predicate),
                                right_predicate)
    second_disjunction = disjoin(left_predicate, disjoin(mid_predicate,
                                                         right_predicate))

    assert (first_disjunction(predicate_argument)
            is second_disjunction(predicate_argument))
