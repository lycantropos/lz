import functools as _functools
import itertools as _itertools
import typing as _t

from ._core.left import Applier as _Applier
from .iterating import expand as _expand

_T1 = _t.TypeVar('_T1')
_T2 = _t.TypeVar('_T2')


def accumulator(
        function: _t.Callable[[_T2, _T1], _T2],
        initial: _T2
) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T2]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from left to right.

    >>> import math
    >>> to_pi_approximations = accumulator(round, math.pi)
    >>> list(to_pi_approximations(_T2(5, 0, -1)))
    [3.141592653589793, 3.14159, 3.1416, 3.142, 3.14, 3.1]
    """
    return _functools.partial(accumulate, function, initial)


def accumulate(function: _t.Callable[[_T2, _T1], _T2],
               initial: _T2,
               iterable: _t.Iterable[_T1]) -> _t.Iterable[_T2]:
    """
    Yields cumulative results of given binary function
    starting from given initial object in direction from left to right.
    """
    yield from _itertools.accumulate(
            attach(iterable, initial),
            _t.cast(_t.Callable[[_t.Any, _t.Any], _T2], function)
    )


def attacher(_value: _T1) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]]:
    """
    Returns function that prepends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [100, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return _functools.partial(attach,
                              _value=_value)


@_functools.singledispatch
def attach(_target: _t.Iterable[_T1], _value: _T1) -> _t.Iterable[_T1]:
    """
    Prepends given value to the target.
    """
    yield from _itertools.chain(_expand(_value), _target)


@attach.register(list)
def _(_target: _t.List[_T1], _value: _T1) -> _t.List[_T1]:
    """
    Prepends given object to the list.
    """
    return [_value] + _target


@attach.register(tuple)
def _(_target: _t.Tuple[_T1, ...], _value: _T1) -> _t.Tuple[_T1, ...]:
    """
    Prepends given value to the tuple.
    """
    return (_value,) + _target


def folder(function: _t.Callable[[_T2, _T1], _T2],
           initial: _T2) -> _t.Callable[[_t.Iterable[_T1]], _T2]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from left to right.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(_T2(1, 10))
    '(((((((((0 + 1) + 2) + 3) + 4) + 5) + 6) + 7) + 8) + 9)'
    """
    return _functools.partial(fold, function, initial)


def fold(function: _t.Callable[[_T2, _T1], _T2],
         initial: _T2,
         iterable: _t.Iterable[_T1]) -> _T2:
    """
    Cumulatively applies given binary function
    starting from given initial object in direction from left to right.
    """
    return _functools.reduce(function, iterable, initial)


def applier(function: _t.Callable[..., _T2],
            *args: _T1,
            **kwargs: _T1) -> _t.Callable[..., _T2]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the left end.

    >>> count_from_zero_to = applier(_T2, 0)
    >>> list(count_from_zero_to(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return _Applier(function, *args, **kwargs)
