import functools
import itertools
from typing import (Iterable,
                    Tuple)

from .functional import (combine,
                         compose)
from .hints import (Domain,
                    Map,
                    Operator,
                    Predicate)
from .replication import duplicate as _duplicate


def sifter(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from iterable
    which satisfy given predicate.

    If predicate is not specified than true-like objects are selected.

    >>> to_true_like = sifter()
    >>> list(to_true_like(range(10)))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> to_even = sifter(is_even)
    >>> list(to_even(range(10)))
    [0, 2, 4, 6, 8]
    """
    return functools.partial(filter, predicate)


def scavenger(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from iterable
    which dissatisfy given predicate.

    If predicate is not specified than false-like objects are selected.

    >>> to_false_like = scavenger()
    >>> list(to_false_like(range(10)))
    [0]

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> to_odd = scavenger(is_even)
    >>> list(to_odd(range(10)))
    [1, 3, 5, 7, 9]
    """
    return functools.partial(itertools.filterfalse, predicate)


def separator(predicate: Predicate = None
              ) -> Map[Iterable[Domain],
                       Tuple[Iterable[Domain], Iterable[Domain]]]:
    """
    Returns function that returns pair of iterables
    first of which consists of elements that dissatisfy given predicate
    and second one consists of elements that satisfy given predicate.

    >>> split_by_truth = separator()
    >>> tuple(map(list, split_by_truth(range(10))))
    ([0], [1, 2, 3, 4, 5, 6, 7, 8, 9])

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> split_by_evenness = separator(is_even)
    >>> tuple(map(list, split_by_evenness(range(10))))
    ([1, 3, 5, 7, 9], [0, 2, 4, 6, 8])
    """
    return compose(tuple,
                   combine(scavenger(predicate), sifter(predicate)),
                   _duplicate)


def grabber(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from the beginning of iterable
    while given predicate is satisfied.

    If predicate is not specified than true-like objects are selected.

    >>> grab_while_true_like = grabber()
    >>> list(grab_while_true_like(range(10)))
    []

    >>> from operator import gt
    >>> from functools import partial
    >>> grab_while_less_than_five = grabber(partial(gt, 5))
    >>> list(grab_while_less_than_five(range(10)))
    [0, 1, 2, 3, 4]
    """
    if predicate is None:
        predicate = bool
    return functools.partial(itertools.takewhile, predicate)


def kicker(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that skips elements from the beginning of iterable
    while given predicate is satisfied.

    If predicate is not specified than true-like objects are skipped.

    >>> kick_while_true_like = kicker()
    >>> list(kick_while_true_like(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> from operator import gt
    >>> from functools import partial
    >>> kick_while_less_than_five = kicker(partial(gt, 5))
    >>> list(kick_while_less_than_five(range(10)))
    [5, 6, 7, 8, 9]
    """
    if predicate is None:
        predicate = bool
    return functools.partial(itertools.dropwhile, predicate)
