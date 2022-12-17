from typing import Callable

from hypothesis import given

from lz.logical import exclusive_disjoin
from tests import strategies
from tests.hints import Domain


@given(strategies.predicates, strategies.predicates_arguments)
def test_idempotency(predicate: Callable[[Domain], bool],
                     predicate_argument: Domain) -> None:
    self_exclusive_disjunction = exclusive_disjoin(predicate)

    result = self_exclusive_disjunction(predicate_argument)

    assert result is predicate(predicate_argument)


@given(strategies.predicates,
       strategies.false_predicates,
       strategies.predicates_arguments)
def test_neutral_element(predicate: Callable[[Domain], bool],
                         false_predicate: Callable[[Domain], bool],
                         predicate_argument: Domain) -> None:
    left_exclusive_disjunction = exclusive_disjoin(predicate, false_predicate)
    right_exclusive_disjunction = exclusive_disjoin(false_predicate, predicate)

    left_result = left_exclusive_disjunction(predicate_argument)
    right_result = right_exclusive_disjunction(predicate_argument)

    assert left_result is right_result is predicate(predicate_argument)


@given(strategies.predicates,
       strategies.predicates,
       strategies.predicates_arguments)
def test_commutativity(left_predicate: Callable[[Domain], bool],
                       right_predicate: Callable[[Domain], bool],
                       predicate_argument: Domain) -> None:
    left_exclusive_disjunction = exclusive_disjoin(left_predicate,
                                                   right_predicate)
    right_exclusive_disjunction = exclusive_disjoin(right_predicate,
                                                    left_predicate)

    left_result = left_exclusive_disjunction(predicate_argument)
    right_result = right_exclusive_disjunction(predicate_argument)

    assert left_result is right_result


@given(strategies.predicates, strategies.predicates, strategies.predicates,
       strategies.predicates_arguments)
def test_associativity(left_predicate: Callable[[Domain], bool],
                       mid_predicate: Callable[[Domain], bool],
                       right_predicate: Callable[[Domain], bool],
                       predicate_argument: Domain) -> None:
    first_exclusive_disjunction = exclusive_disjoin(
            exclusive_disjoin(left_predicate, mid_predicate), right_predicate
    )
    second_exclusive_disjunction = exclusive_disjoin(
            left_predicate, exclusive_disjoin(mid_predicate, right_predicate)
    )

    assert (first_exclusive_disjunction(predicate_argument)
            is second_exclusive_disjunction(predicate_argument))
