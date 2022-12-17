import functools
import itertools
import sys
from typing import (Callable,
                    Iterable,
                    Iterator,
                    List,
                    Tuple, 
                    TypeVar)

from ._core.left import Applier
from .iterating import expand

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')


def accumulator(
        function: Callable[[_T2, _T1], _T2],
        initial: _T2
) -> Callable[[Iterable[_T1]], Iterable[_T2]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from left to right.

    >>> import math
    >>> to_pi_approximations = accumulator(round, math.pi)
    >>> list(to_pi_approximations(_T2(5, 0, -1)))
    [3.141592653589793, 3.14159, 3.1416, 3.142, 3.14, 3.1]
    """
    return functools.partial(accumulate, function, initial)


if sys.version_info < (3, 8):
    def accumulate(function: Callable[[_T2, _T1], _T2],
                   initial: _T2,
                   iterable: Iterable[_T1]) -> Iterator[_T2]:
        """
        Yields cumulative results of given binary function
        starting from given initial object in direction from left to right.
        """
        yield from itertools.accumulate(attach(iterable, initial), function)
else:
    def accumulate(function: Callable[[_T2, _T1], _T2],
                   initial: _T2,
                   iterable: Iterable[_T1]) -> Iterator[_T2]:
        """
        Yields cumulative results of given binary function
        starting from given initial object in direction from left to right.
        """
        yield from itertools.accumulate(iterable, function,
                                        initial=initial)


def attacher(_value: _T1) -> Callable[[Iterable[_T1]], Iterable[_T1]]:
    """
    Returns function that prepends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [100, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return functools.partial(attach,
                             _value=_value)


@functools.singledispatch
def attach(_target: Iterable[_T1], _value: _T1) -> Iterable[_T1]:
    """
    Prepends given value to the target.
    """
    yield from itertools.chain(expand(_value), _target)


@attach.register(list)
def _(_target: List[_T1], _value: _T1) -> List[_T1]:
    """
    Prepends given object to the list.
    """
    return [_value] + _target


@attach.register(tuple)
def _(_target: Tuple[_T1, ...], _value: _T1) -> Tuple[_T1, ...]:
    """
    Prepends given value to the tuple.
    """
    return (_value,) + _target


def folder(function: Callable[[_T2, _T1], _T2],
           initial: _T2) -> Callable[[Iterable[_T1]], _T2]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from left to right.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(_T2(1, 10))
    '(((((((((0 + 1) + 2) + 3) + 4) + 5) + 6) + 7) + 8) + 9)'
    """
    return functools.partial(fold, function, initial)


def fold(function: Callable[[_T2, _T1], _T2],
         initial: _T2,
         iterable: Iterable[_T1]) -> _T2:
    """
    Cumulatively applies given binary function
    starting from given initial object in direction from left to right.
    """
    return functools.reduce(function, iterable, initial)


def applier(function: Callable[..., _T2],
            *args: _T1,
            **kwargs: _T1) -> Callable[..., _T2]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the left end.

    >>> count_from_zero_to = applier(_T2, 0)
    >>> list(count_from_zero_to(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return Applier(function, *args, **kwargs)
