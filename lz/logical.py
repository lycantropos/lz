from operator import (not_,
                      xor)

from . import left
from .functional import (cleave,
                         compose)
from .hints import Predicate


def conjoin(*predicates: Predicate) -> Predicate:
    """
    Returns conjunction of given predicates.

    >>> is_valid_constant_identifier = conjoin(str.isupper, str.isidentifier)
    >>> is_valid_constant_identifier('SECOND_SECTION')
    True
    >>> is_valid_constant_identifier('2ND_SECTION')
    False
    """
    return compose(all, cleave(*predicates))


def disjoin(*predicates: Predicate) -> Predicate:
    """
    Returns disjunction of given predicates.

    >>> alphabetic_or_numeric = disjoin(str.isalpha, str.isnumeric)
    >>> alphabetic_or_numeric('Hello')
    True
    >>> alphabetic_or_numeric('42')
    True
    >>> alphabetic_or_numeric('Hello42')
    False
    """
    return compose(any, cleave(*predicates))


def exclusive_disjoin(*predicates: Predicate) -> Predicate:
    """
    Returns exclusive disjunction of given predicates.

    >>> from keyword import iskeyword
    >>> valid_object_name = exclusive_disjoin(str.isidentifier, iskeyword)
    >>> valid_object_name('valid_object_name')
    True
    >>> valid_object_name('_')
    True
    >>> valid_object_name('1')
    False
    >>> valid_object_name('lambda')
    False
    """
    return compose(left.folder(xor, False), cleave(*predicates))


def negate(predicate: Predicate) -> Predicate:
    """
    Returns negated version of given predicate.

    >>> from lz.logical import negate
    >>> false_like = negate(bool)
    >>> false_like([])
    True
    >>> false_like([0])
    False
    """
    return compose(not_, predicate)
