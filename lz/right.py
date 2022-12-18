import functools as _functools
import itertools as _itertools
import typing as _t

from . import left as _left
from ._core.right import Applier as _Applier
from .functional import (compose as _compose,
                         flip as _flip)
from .iterating import expand as _expand
from .reversal import reverse as _reverse

_T1 = _t.TypeVar('_T1')
_T2 = _t.TypeVar('_T2')


def accumulator(
        _function: _t.Callable[[_T1, _T2], _T2], _initial: _T2
) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_t.Iterable[_T2]]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from right to left.

    >>> def to_next_fraction(partial_denominator: int,
    ...                      reciprocal: float) -> float:
    ...     return partial_denominator + 1 / reciprocal
    >>> to_simple_continued_fractions = accumulator(to_next_fraction, 1)
    >>> from itertools import repeat
    >>> [round(fraction, 4)
    ...  for fraction in to_simple_continued_fractions(list(repeat(1, 10)))]
    [1, 2.0, 1.5, 1.6667, 1.6, 1.625, 1.6154, 1.619, 1.6176, 1.6182, 1.618]
    """
    return _t.cast(_t.Callable[[_t.Iterable[_T1]],
                               _t.Iterable[_t.Iterable[_T2]]],
                   _compose(_left.accumulator(_flip(_function), _initial),
                            _reverse))


def accumulate(_function: _t.Callable[[_T1, _T2], _T2],
               _initial: _T2,
               _iterable: _t.Iterable[_T1]) -> _t.Iterable[_T2]:
    """
    Yields cumulative results of given binary function
    starting from given initial object in direction from right to left.

    >>> def to_next_fraction(partial_denominator: int,
    ...                      reciprocal: float) -> float:
    ...     return partial_denominator + 1 / reciprocal
    >>> from itertools import repeat
    >>> [round(fraction, 4)
    ...  for fraction in accumulate(to_next_fraction, 1, list(repeat(1, 10)))]
    [1, 2.0, 1.5, 1.6667, 1.6, 1.625, 1.6154, 1.619, 1.6176, 1.6182, 1.618]
    """
    return _left.accumulate(_flip(_function), _initial, _reverse(_iterable))


def attacher(_value: _T1) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]]:
    """
    Returns function that appends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    """
    return _t.cast(_t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]],
                   _Applier(attach, _value))


@_functools.singledispatch
def attach(_iterable: _t.Iterable[_T1], _value: _T1) -> _t.Iterable[_T1]:
    """
    Appends given object to the iterable.
    """
    yield from _itertools.chain(_iterable, _expand(_value))


@attach.register(list)
def _(_iterable: _t.List[_T1], _value: _T1) -> _t.List[_T1]:
    """
    Appends given object to the list.
    """
    return _iterable + [_value]


@attach.register(tuple)
def _(_iterable: _t.Tuple[_T1, ...], _value: _T1) -> _t.Tuple[_T1, ...]:
    """
    Appends given object to the tuple.
    """
    return _iterable + (_value,)


def folder(_function: _t.Callable[[_T1, _T2], _T2],
           _initial: _T2) -> _t.Callable[[_t.Iterable[_T1]], _T2]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from right to left.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(range(1, 10))
    '(1 + (2 + (3 + (4 + (5 + (6 + (7 + (8 + (9 + 0)))))))))'
    """
    left_folder = _left.folder(_flip(_function), _initial)
    return _compose(left_folder, _reverse)


def fold(_function: _t.Callable[[_T2, _T1], _T2],
         _initial: _T2,
         _iterable: _t.Iterable[_T1]) -> _T2:
    """
    Cumulatively applies given binary function
    starting from given initial object in direction from left to right.

    >>> fold('({} + {})'.format, 0, range(1, 10))
    '(1 + (2 + (3 + (4 + (5 + (6 + (7 + (8 + (9 + 0)))))))))'
    """
    return _functools.reduce(_flip(_function), _reverse(_iterable), _initial)


def applier(_function: _t.Callable[..., _T2],
            *args: _t.Any,
            **kwargs: _t.Any) -> _t.Callable[..., _T2]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the right end.

    >>> square = applier(pow, 2)
    >>> square(10)
    100
    """
    return _Applier(_function, *args, **kwargs)
