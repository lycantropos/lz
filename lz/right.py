import functools
import itertools
from typing import (Callable,
                    Iterable,
                    List,
                    Tuple)

from reprit.base import generate_repr

from . import left
from .functional import (ApplierBase,
                         compose,
                         flip)
from .hints import (Domain,
                    Map,
                    Range)
from .iterating import expand
from .reversal import reverse


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
    return functools.partial(attach,
                             object_=object_)


@functools.singledispatch
def attach(iterable: Iterable[Domain],
           object_: Domain) -> Iterable[Domain]:
    yield from itertools.chain(iterable, expand(object_))


@attach.register(list)
def attach_to_list(iterable: List[Domain],
                   object_: Domain) -> List[Domain]:
    return iterable + [object_]


@attach.register(tuple)
def attach_to_tuple(iterable: Tuple[Domain, ...],
                    object_: Domain) -> Tuple[Domain, ...]:
    return iterable + (object_,)


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

    __repr__ = generate_repr(__init__)


def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the right end.
    """

    return Applier(function, *args, **kwargs)
