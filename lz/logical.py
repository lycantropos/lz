import typing as _t
from operator import (not_,
                      xor)

import typing_extensions as _te

from . import left as _left
from .functional import (cleave as _cleave,
                         compose as _compose)

_Params = _te.ParamSpec('_Params')
_T = _t.TypeVar('_T')


def conjoin(
        *predicates: _t.Callable[_Params, bool]
) -> _t.Callable[_Params, bool]:
    """
    Returns conjunction of given predicates.

    >>> is_valid_constant_identifier = conjoin(str.isupper, str.isidentifier)
    >>> is_valid_constant_identifier('SECOND_SECTION')
    True
    >>> is_valid_constant_identifier('2ND_SECTION')
    False
    """
    return _compose(all, _cleave(*predicates))


def disjoin(
        *predicates: _t.Callable[_Params, bool]
) -> _t.Callable[_Params, bool]:
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
    return _compose(any, _cleave(*predicates))


def exclusive_disjoin(
        *predicates: _t.Callable[_Params, bool]
) -> _t.Callable[_Params, bool]:
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
    return _compose(_left.folder(xor, False), _cleave(*predicates))


def negate(
        predicate: _t.Callable[_Params, bool]
) -> _t.Callable[_Params, bool]:
    """
    Returns negated version of given predicate.

    >>> false_like = negate(bool)
    >>> false_like([])
    True
    >>> false_like([0])
    False
    """
    return _compose(not_, predicate)
