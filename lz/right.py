import itertools
from typing import (Callable,
                    Iterable)

from . import left
from .functional import (compose,
                         flip)
from .hints import (Domain,
                    Map,
                    Range)
from .iterating import (expand,
                        reverse)


def accumulator(function: Callable[[Domain, Range], Range],
                initial: Range
                ) -> Map[Iterable[Domain], Iterable[Iterable[Range]]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from right to left.
    """
    left_accumulator = left.accumulator(flip(function), initial)
    return compose(left_accumulator, reverse)


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    """
    Returns function that appends given object to iterable.
    """

    def attach(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from itertools.chain(iterable, expand(object_))

    return attach


def folder(function: Callable[[Domain, Range], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from right to left.
    """
    left_folder = left.folder(flip(function), initial)
    return compose(left_folder, reverse)
