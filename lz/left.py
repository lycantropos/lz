import functools
import itertools
from typing import (Callable,
                    Iterable)

from .base import expand
from .hints import (Domain,
                    Map,
                    Range)


def accumulator(function: Callable[[Range, Domain], Range],
                initial: Range
                ) -> Map[Iterable[Domain], Iterable[Range]]:
    attach_initial = attacher(initial)

    def accumulate(iterable: Iterable[Domain]) -> Iterable[Range]:
        yield from itertools.accumulate(attach_initial(iterable), function)

    return accumulate


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    def attach(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from itertools.chain(expand(object_), iterable)

    return attach


def folder(function: Callable[[Range, Domain], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    def fold(iterable: Iterable[Domain]) -> Range:
        return functools.reduce(function, iterable, initial)

    return fold
