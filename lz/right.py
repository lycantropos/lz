import functools
import itertools
from typing import (Callable,
                    Iterable,
                    List,
                    Tuple)

from . import left
from ._core.right import Applier
from .functional import (compose,
                         flip)
from .hints import (Domain,
                    Range)
from .iterating import expand
from .reversal import reverse


def accumulator(
        function: Callable[[Domain, Range], Range],
        initial: Range
) -> Callable[[Iterable[Domain]], Iterable[Iterable[Range]]]:
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
    left_accumulator = left.accumulator(flip(function), initial)
    return compose(left_accumulator, reverse)


def attacher(_value: Domain) -> Callable[[Iterable[Domain]], Iterable[Domain]]:
    """
    Returns function that appends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    """
    return Applier(attach, _value)


@functools.singledispatch
def attach(iterable: Iterable[Domain], _value: Domain) -> Iterable[Domain]:
    """
    Appends given object to the iterable.
    """
    yield from itertools.chain(iterable, expand(_value))


@attach.register(list)
def _(iterable: List[Domain], _value: Domain) -> List[Domain]:
    """
    Appends given object to the list.
    """
    return iterable + [_value]


@attach.register(tuple)
def _(iterable: Tuple[Domain, ...], object_: Domain) -> Tuple[Domain, ...]:
    """
    Appends given object to the tuple.
    """
    return iterable + (object_,)


def folder(function: Callable[[Domain, Range], Range],
           initial: Range) -> Callable[[Iterable[Domain]], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from right to left.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(range(1, 10))
    '(1 + (2 + (3 + (4 + (5 + (6 + (7 + (8 + (9 + 0)))))))))'
    """
    left_folder = left.folder(flip(function), initial)
    return compose(left_folder, reverse)


def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the right end.

    >>> square = applier(pow, 2)
    >>> square(10)
    100
    """
    return Applier(function, *args, **kwargs)
