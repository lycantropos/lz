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
from .replication import duplicate


def sifter(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from iterable
    which satisfy given predicate.

    If predicate is not specified than true-like objects are selected.
    """
    return functools.partial(filter, predicate)


def scavenger(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from iterable
    which dissatisfy given predicate.

    If predicate is not specified than false-like objects are selected.
    """
    return functools.partial(itertools.filterfalse, predicate)


def separator(predicate: Predicate = None
              ) -> Map[Iterable[Domain],
                       Tuple[Iterable[Domain], Iterable[Domain]]]:
    """
    Returns function that returns pair of iterables
    first of which consists of elements that dissatisfy given predicate
    and second one consists of elements that satisfy given predicate.
    """
    return compose(tuple,
                   combine(scavenger(predicate), sifter(predicate)),
                   duplicate)


def grabber(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from the beginning of iterable
    while given predicate is satisfied.

    If predicate is not specified than true-like objects are selected.
    """
    if predicate is None:
        predicate = bool
    return functools.partial(itertools.takewhile, predicate)


def kicker(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that skips elements from the beginning of iterable
    while given predicate is satisfied.

    If predicate is not specified than true-like objects are skipped.
    """
    if predicate is None:
        predicate = bool
    return functools.partial(itertools.dropwhile, predicate)
