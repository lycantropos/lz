import itertools
from typing import (Callable,
                    Iterable)

from . import left
from .functional import (ApplierBase,
                         compose,
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


class Applier(ApplierBase):
    def __init__(self, function: Callable[..., Range],
                 *args: Domain,
                 **kwargs: Domain) -> None:
        super().__init__(function, *args, **kwargs)

    def __call__(self, *args: Domain, **kwargs: Domain) -> Range:
        return self.func(*args, *self.args, **self.keywords, **kwargs)


def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the right end.
    """

    return Applier(function, *args, **kwargs)
