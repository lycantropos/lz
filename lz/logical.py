from operator import not_

from .functional import compose
from .hints import Predicate


def negate(predicate: Predicate) -> Predicate:
    """
    Returns negated version of given predicate.
    """
    return compose(not_, predicate)
