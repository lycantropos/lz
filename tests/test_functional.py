from lz.functional import negate
from lz.hints import Predicate


def test_negate(false_predicate: Predicate,
                true_predicate: Predicate) -> None:
    negated_false_predicate = negate(false_predicate)
    negated_true_predicate = negate(true_predicate)

    assert negated_false_predicate(None)
    assert not negated_true_predicate(None)
