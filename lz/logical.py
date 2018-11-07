from operator import (not_,
                      xor)

from . import left
from .functional import (cleave,
                         compose)
from .hints import Predicate


def conjoin(*predicates: Predicate) -> Predicate:
    """
    Returns conjunction of given predicates.
    """
    return compose(all, cleave(predicates))


def disjoin(*predicates: Predicate) -> Predicate:
    """
    Returns disjunction of given predicates.
    """
    return compose(any, cleave(predicates))


def exclusive_disjoin(*predicates: Predicate) -> Predicate:
    """
    Returns exclusive disjunction of given predicates.
    """
    return compose(left.folder(xor, False), cleave(predicates))


def negate(predicate: Predicate) -> Predicate:
    """
    Returns negated version of given predicate.
    """
    return compose(not_, predicate)
