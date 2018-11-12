import functools
import itertools
from typing import (Callable,
                    Iterable)

from .functional import ApplierBase
from .hints import (Domain,
                    Map,
                    Range)
from .iterating import expand


def accumulator(function: Callable[[Range, Domain], Range],
                initial: Range
                ) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from left to right.
    """
    attach_initial = attacher(initial)

    def accumulate(iterable: Iterable[Domain]) -> Iterable[Range]:
        yield from itertools.accumulate(attach_initial(iterable), function)

    return accumulate


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    """
    Returns function that prepends given object to iterable.
    """

    def attach(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from itertools.chain(expand(object_), iterable)

    return attach


def folder(function: Callable[[Range, Domain], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from left to right.
    """

    def fold(iterable: Iterable[Domain]) -> Range:
        return functools.reduce(function, iterable, initial)

    return fold


Applier = ApplierBase.register(functools.partial)


def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the left end.
    """
    return Applier(function, *args, **kwargs)
