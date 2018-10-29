from operator import not_

from .functional import (cleave,
                         compose)
from .hints import Predicate


def conjoin(*predicates: Predicate) -> Predicate:
    """
    Returns conjunction of given predicates.
    """
    return compose(all, cleave(predicates))


def negate(predicate: Predicate) -> Predicate:
    """
    Returns negated version of given predicate.
    """
    return compose(not_, predicate)
