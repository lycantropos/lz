import functools
import itertools
import typing as _t

from . import left
from ._core.right import Applier
from .functional import (compose,
                         flip)
from .iterating import expand
from .reversal import reverse

_T1 = _t.TypeVar('_T1')
_T2 = _t.TypeVar('_T2')


def accumulator(
        function: _t.Callable[[_T1, _T2], _T2], initial: _T2
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
                   compose(left.accumulator(flip(function), initial), reverse))


def attacher(_value: _T1) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]]:
    """
    Returns function that appends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    """
    return _t.cast(_t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]],
                   Applier(attach, _value))


@functools.singledispatch
def attach(_iterable: _t.Iterable[_T1], _value: _T1) -> _t.Iterable[_T1]:
    """
    Appends given object to the iterable.
    """
    yield from itertools.chain(_iterable, expand(_value))


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
    left_folder = left.folder(flip(_function), _initial)
    return compose(left_folder, reverse)


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
    return Applier(_function, *args, **kwargs)
