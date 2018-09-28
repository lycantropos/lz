import functools
import itertools
from collections import defaultdict
from typing import (Hashable,
                    Iterable,
                    List,
                    Mapping,
                    Reversible,
                    Tuple,
                    Union)

from .functional import compose
from .hints import (Domain,
                    Map,
                    Operator,
                    Predicate,
                    Range,
                    Sortable)


def mapper(map_: Map) -> Map[Iterable[Domain], Iterable[Range]]:
    return functools.partial(map, map_)


def sifter(predicate: Predicate = None) -> Operator[Iterable[Domain]]:
    return functools.partial(filter, predicate)


def cutter(slice_: slice) -> Map[Iterable[Domain], Iterable[Domain]]:
    start = slice_.start
    stop = slice_.stop
    step = slice_.step

    def cut(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from itertools.islice(iterable, start, stop, step)

    return cut


def chopper(size: int) -> Map[Iterable[Domain], Iterable[Tuple[Domain, ...]]]:
    def chop(iterable: Iterable[Domain]) -> Iterable[Tuple[Domain, ...]]:
        iterator = iter(iterable)
        yield from zip(*itertools.repeat(iterator, size))

    return chop


def slider(size: int) -> Map[Iterable[Domain], Iterable[Tuple[Domain, ...]]]:
    def slide(iterable: Iterable[Domain]) -> Iterable[Tuple[Domain, ...]]:
        iterator = iter(iterable)
        result = tuple(itertools.islice(iterator, size))
        if len(result) < size:
            raise ValueError('Iterable should have size '
                             'not less than {min_size}, '
                             'but found {actual_size}.'
                             .format(min_size=size,
                                     actual_size=len(result)))

        def shift(previous: Tuple[Domain, ...],
                  element: Domain) -> Tuple[Domain, ...]:
            return previous[1:] + (element,)

        yield from itertools.accumulate(itertools.chain([result], iterator),
                                        shift)

    return slide


def sorter(key: Map[Domain, Sortable] = None
           ) -> Map[Iterable[Domain], Iterable[Domain]]:
    def sort(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from sorted(iterable,
                          key=key)

    return sort


Group = Tuple[Hashable, Iterable[Domain]]


def grouper(key: Map[Domain, Hashable]
            ) -> Map[Iterable[Domain], Iterable[Group]]:
    def group_by(iterable: Iterable[Domain]) -> Iterable[Group]:
        groups = defaultdict(list)  # type: Mapping[Hashable, List[Domain]]
        for element in iterable:
            groups[key(element)].append(element)
        yield from groups.items()

    return group_by


def reverse(iterable: Union[Reversible[Domain],
                            Iterable[Domain]]) -> Iterable[Domain]:
    try:
        result = reversed(iterable)
    except TypeError:
        result = reversed(list(iterable))
    yield from result


def expand(object_: Domain) -> Iterable[Domain]:
    yield object_


def flatten(iterable: Iterable[Iterable[Domain]]) -> Iterable[Domain]:
    return itertools.chain.from_iterable(iterable)


def flatmapper(map_: Map[Domain, Iterable[Range]]
               ) -> Map[Iterable[Domain], Iterable[Range]]:
    return compose(flatten, mapper(map_))


def copier(count: int) -> Map[Iterable[Domain], Iterable[Iterable[Domain]]]:
    min_count = 0
    if count < min_count:
        raise ValueError('Count should be '
                         'not less than {min_count}, '
                         'but found {actual_count}.'
                         .format(min_count=min_count,
                                 actual_count=count))

    def copy(iterable: Iterable[Domain]) -> Iterable[Iterable[Domain]]:
        yield from itertools.tee(iterable, count)

    return copy
