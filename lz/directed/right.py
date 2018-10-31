import functools
import itertools
from typing import (Callable,
                    Iterable)

from lz.functional import (compose,
                           flip)
from lz.hints import (Domain,
                      Map,
                      Range)
from lz.iterating import (expand,
                          reverse)
from . import (common,
               left)


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


def applier(function: Callable[..., Range],
            *applied_args: Domain,
            **applied_kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Positional arguments will be applied from the right end.
    """
    start = step = -1

    def to_rest_start(occupied_indices: Iterable[int]) -> int:
        return min(occupied_indices,
                   default=start) + step

    complete_args = common.to_applier_flow(applied_args,
                                           start=start,
                                           step=step,
                                           rest_start_factory=to_rest_start)

    @functools.wraps(function)
    def applied(*args, **kwargs) -> Range:
        return function(*complete_args(reverse(args)),
                        **applied_kwargs,
                        **kwargs)

    return applied
