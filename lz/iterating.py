import functools
import itertools
from collections import (abc,
                         defaultdict,
                         deque)
from operator import is_not
from typing import (Hashable,
                    Iterable,
                    List,
                    Mapping,
                    Sequence,
                    Tuple)

from .functional import (combine,
                         compose)
from .hints import (Domain,
                    Map,
                    Operator,
                    Predicate,
                    Range)
from .replication import duplicate


def mapper(map_: Map) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies given map to the each element of iterable.
    """
    return functools.partial(map, map_)


def flatmapper(map_: Map[Domain, Iterable[Range]]
               ) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies map to the each element of iterable
    and flattens results.
    """
    return compose(flatten, mapper(map_))


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
                   combine([scavenger(predicate), sifter(predicate)]),
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


def cutter(slice_: slice) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from iterable based on given slice.

    Slice fields supposed to be unset or non-negative
    since it is hard to evaluate negative indices/step for arbitrary iterable
    which may be potentially infinite
    or change previous elements if iterating made backwards.
    """
    start = slice_.start
    stop = slice_.stop
    step = slice_.step

    def cut(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from itertools.islice(iterable, start, stop, step)

    return cut


def chopper(size: int) -> Map[Iterable[Domain], Iterable[Sequence[Domain]]]:
    """
    Returns function that splits iterable into chunks of given size.
    """

    @functools.singledispatch
    def chop(iterable: Iterable[Domain]) -> Iterable[Sequence[Domain]]:
        iterator = iter(iterable)
        yield from iter(lambda: tuple(itertools.islice(iterator, size)), ())

    @chop.register(abc.Sequence)
    def chop_sequence(iterable: Sequence[Domain]
                      ) -> Iterable[Sequence[Domain]]:
        for start in range(0, len(iterable), size):
            yield iterable[start:start + size]

    return chop


def slider(size: int) -> Map[Iterable[Domain], Iterable[Tuple[Domain, ...]]]:
    """
    Returns function that slides over iterable with window of given size.
    """

    def slide(iterable: Iterable[Domain]) -> Iterable[Tuple[Domain, ...]]:
        iterator = iter(iterable)
        initial = tuple(itertools.islice(iterator, size))

        def shift(previous: Tuple[Domain, ...],
                  element: Domain) -> Tuple[Domain, ...]:
            return previous[1:] + (element,)

        yield from itertools.accumulate(itertools.chain([initial], iterator),
                                        shift)

    return slide


Group = Tuple[Hashable, Iterable[Domain]]


def grouper(key: Map[Domain, Hashable]
            ) -> Map[Iterable[Domain], Iterable[Group]]:
    """
    Returns function that groups iterable elements based on given key.
    """

    def group_by(iterable: Iterable[Domain]) -> Iterable[Group]:
        groups = defaultdict(list)  # type: Mapping[Hashable, List[Domain]]
        for element in iterable:
            groups[key(element)].append(element)
        yield from groups.items()

    return group_by


def expand(object_: Domain) -> Iterable[Domain]:
    """
    Wraps object into iterable.
    """
    yield object_


def interleave(iterable: Iterable[Iterable[Domain]]) -> Iterable[Domain]:
    """
    Interleaves elements from given iterable of iterables.
    """
    iterators = itertools.cycle(map(iter, iterable))
    while True:
        try:
            for iterator in iterators:
                yield next(iterator)
        except StopIteration:
            is_not_exhausted = functools.partial(is_not, iterator)
            iterators = itertools.cycle(itertools.takewhile(is_not_exhausted,
                                                            iterators))
        else:
            return


def flatten(iterable: Iterable[Iterable[Domain]]) -> Iterable[Domain]:
    """
    Returns plain iterable from iterable of iterables.
    """
    yield from itertools.chain.from_iterable(iterable)


def header(size: int) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from the beginning of iterable.
    Resulted iterable will have size not greater than given one.
    """
    return cutter(slice(size))


first = compose(next, iter)
first.__doc__ = 'Returns first element of iterable.'


def trailer(size: int) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from the end of iterable.
    Resulted iterable will have size not greater than given one.
    """
    return compose(iter,
                   functools.partial(deque,
                                     maxlen=size))


last = compose(next, trailer(1))
last.__doc__ = 'Returns last element of iterable.'
