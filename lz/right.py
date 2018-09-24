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
    left_accumulator = left.accumulator(flip(function), initial)
    return compose(left_accumulator, reverse)


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    def attach(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from itertools.chain(iterable, expand(object_))

    return attach


def folder(function: Callable[[Domain, Range], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    left_folder = left.folder(flip(function), initial)
    return compose(left_folder, reverse)
