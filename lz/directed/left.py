import functools
import itertools
from typing import (Callable,
                    Iterable)

from lz.hints import (Domain,
                      Map,
                      Range)
from lz.iterating import expand
from . import common


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


def applier(function: Callable[..., Range],
            *applied_args: Domain,
            **applied_kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Positional arguments will be applied from the left end.
    """
    start = 0
    step = 1

    def to_rest_start(occupied_indices: Iterable[int]) -> int:
        return max(occupied_indices,
                   default=start) + step

    complete_args = common.to_applier_flow(applied_args,
                                           start=start,
                                           step=step,
                                           rest_start_factory=to_rest_start)

    @functools.wraps(function)
    def applied(*args, **kwargs) -> Range:
        return function(*complete_args(args), **applied_kwargs, **kwargs)

    return applied
