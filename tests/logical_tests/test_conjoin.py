from typing import Callable

from hypothesis import given

from lz.logical import conjoin
from tests import strategies
from tests.hints import Domain


@given(strategies.predicates, strategies.predicates_arguments)
def test_idempotency(predicate: Callable[[Domain], bool],
                     predicate_argument: Domain) -> None:
    self_conjunction = conjoin(predicate)

    result = self_conjunction(predicate_argument)

    assert result is predicate(predicate_argument)


@given(strategies.predicates, strategies.false_predicates,
       strategies.predicates_arguments)
def test_absorbing_element(predicate: Callable[[Domain], bool],
                           false_predicate: Callable[[Domain], bool],
                           predicate_argument: Domain) -> None:
    left_conjunction = conjoin(predicate, false_predicate)
    right_conjunction = conjoin(false_predicate, predicate)

    left_result = left_conjunction(predicate_argument)
    right_result = right_conjunction(predicate_argument)

    assert left_result is right_result is false_predicate(predicate_argument)


@given(strategies.predicates, strategies.true_predicates,
       strategies.predicates_arguments)
def test_neutral_element(predicate: Callable[[Domain], bool],
                         true_predicate: Callable[[Domain], bool],
                         predicate_argument: Domain) -> None:
    left_conjunction = conjoin(predicate, true_predicate)
    right_conjunction = conjoin(true_predicate, predicate)

    left_result = left_conjunction(predicate_argument)
    right_result = right_conjunction(predicate_argument)

    assert left_result is right_result is predicate(predicate_argument)


@given(strategies.predicates, strategies.predicates,
       strategies.predicates_arguments)
def test_commutativity(left_predicate: Callable[[Domain], bool],
                       right_predicate: Callable[[Domain], bool],
                       predicate_argument: Domain) -> None:
    left_conjunction = conjoin(left_predicate, right_predicate)
    right_conjunction = conjoin(right_predicate, left_predicate)

    left_result = left_conjunction(predicate_argument)
    right_result = right_conjunction(predicate_argument)

    assert left_result is right_result


@given(strategies.predicates, strategies.predicates, strategies.predicates,
       strategies.predicates_arguments)
def test_associativity(left_predicate: Callable[[Domain], bool],
                       mid_predicate: Callable[[Domain], bool],
                       right_predicate: Callable[[Domain], bool],
                       predicate_argument: Domain) -> None:
    first_conjunction = conjoin(conjoin(left_predicate, mid_predicate),
                                right_predicate)
    second_conjunction = conjoin(left_predicate,
                                 conjoin(mid_predicate, right_predicate))

    assert (first_conjunction(predicate_argument)
            is second_conjunction(predicate_argument))
