import functools
import itertools
import sys
from typing import (Callable,
                    Iterable,
                    Iterator,
                    List,
                    Tuple)

from ._core.left import Applier
from .hints import (Domain,
                    Range)
from .iterating import expand


def accumulator(
        function: Callable[[Range, Domain], Range],
        initial: Range
) -> Callable[[Iterable[Domain]], Iterable[Range]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from left to right.

    >>> import math
    >>> to_pi_approximations = accumulator(round, math.pi)
    >>> list(to_pi_approximations(range(5, 0, -1)))
    [3.141592653589793, 3.14159, 3.1416, 3.142, 3.14, 3.1]
    """
    return functools.partial(accumulate, function, initial)


if sys.version_info < (3, 8):
    def accumulate(function: Callable[[Range, Domain], Range],
                   initial: Range,
                   iterable: Iterable[Domain]) -> Iterator[Range]:
        """
        Yields cumulative results of given binary function
        starting from given initial object in direction from left to right.
        """
        yield from itertools.accumulate(attach(iterable, initial), function)
else:
    def accumulate(function: Callable[[Range, Domain], Range],
                   initial: Range,
                   iterable: Iterable[Domain]) -> Iterator[Range]:
        """
        Yields cumulative results of given binary function
        starting from given initial object in direction from left to right.
        """
        yield from itertools.accumulate(iterable, function,
                                        initial=initial)


def attacher(_value: Domain) -> Callable[[Iterable[Domain]], Iterable[Domain]]:
    """
    Returns function that prepends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [100, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return functools.partial(attach,
                             _value=_value)


@functools.singledispatch
def attach(_target: Iterable[Domain], _value: Domain) -> Iterable[Domain]:
    """
    Prepends given value to the target.
    """
    yield from itertools.chain(expand(_value), _target)


@attach.register(list)
def _(_target: List[Domain], _value: Domain) -> List[Domain]:
    """
    Prepends given object to the list.
    """
    return [_value] + _target


@attach.register(tuple)
def _(_target: Tuple[Domain, ...], _value: Domain) -> Tuple[Domain, ...]:
    """
    Prepends given value to the tuple.
    """
    return (_value,) + _target


def folder(function: Callable[[Range, Domain], Range],
           initial: Range) -> Callable[[Iterable[Domain]], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from left to right.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(range(1, 10))
    '(((((((((0 + 1) + 2) + 3) + 4) + 5) + 6) + 7) + 8) + 9)'
    """
    return functools.partial(fold, function, initial)


def fold(function: Callable[[Range, Domain], Range],
         initial: Range,
         iterable: Iterable[Domain]) -> Range:
    """
    Cumulatively applies given binary function
    starting from given initial object in direction from left to right.
    """
    return functools.reduce(function, iterable, initial)


def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the left end.

    >>> count_from_zero_to = applier(range, 0)
    >>> list(count_from_zero_to(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return Applier(function, *args, **kwargs)
