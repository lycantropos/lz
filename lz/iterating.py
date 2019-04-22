import functools
import itertools
from collections import (abc,
                         defaultdict,
                         deque)
from functools import singledispatch
from operator import is_not
from typing import (Any,
                    Hashable,
                    Iterable,
                    List,
                    Mapping,
                    Sequence,
                    Sized,
                    Tuple)

from .functional import compose
from .hints import (Domain,
                    Map,
                    Operator,
                    Range)


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


def cutter(slice_: slice) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from iterable based on given slice.
    """
    return functools.partial(cut,
                             slice_=slice_)


def cut(iterable: Iterable[Domain],
        *,
        slice_: slice) -> Iterable[Domain]:
    """
    Selects elements from iterable based on given slice.

    Slice fields supposed to be unset or non-negative
    since it is hard to evaluate negative indices/step for arbitrary iterable
    which may be potentially infinite
    or change previous elements if iterating made backwards.
    """
    yield from itertools.islice(iterable,
                                slice_.start, slice_.stop, slice_.step)


def chopper(size: int) -> Map[Iterable[Domain], Iterable[Sequence[Domain]]]:
    """
    Returns function that splits iterable into chunks of given size.
    """
    return functools.partial(chop,
                             size=size)


@functools.singledispatch
def chop(iterable: Iterable[Domain],
         *,
         size: int) -> Iterable[Sequence[Domain]]:
    """
    Splits iterable into chunks of given size.
    """
    iterator = iter(iterable)
    yield from iter(lambda: tuple(itertools.islice(iterator, size)), ())


@chop.register(abc.Sequence)
def chop_sequence(iterable: Sequence[Domain],
                  *,
                  size: int) -> Iterable[Sequence[Domain]]:
    """
    Splits sequence into chunks of given size.
    """
    if not size:
        return
    for start in range(0, len(iterable), size):
        yield iterable[start:start + size]


def slider(size: int) -> Map[Iterable[Domain], Iterable[Tuple[Domain, ...]]]:
    """
    Returns function that slides over iterable with window of given size.
    """
    return functools.partial(slide,
                             size=size)


def slide(iterable: Iterable[Domain],
          *,
          size: int) -> Iterable[Tuple[Domain, ...]]:
    """
    Slides over iterable with window of given size.
    """
    iterator = iter(iterable)
    initial = tuple(itertools.islice(iterator, size))

    def shift(previous: Tuple[Domain, ...],
              element: Domain) -> Tuple[Domain, ...]:
        return previous[1:] + (element,)

    yield from itertools.accumulate(itertools.chain([initial], iterator),
                                    shift)


Group = Tuple[Hashable, Iterable[Domain]]


def grouper(key: Map[Domain, Hashable]
            ) -> Map[Iterable[Domain], Iterable[Group]]:
    """
    Returns function that groups iterable elements based on given key.
    """
    return functools.partial(group_by,
                             key=key)


def group_by(iterable: Iterable[Domain],
             *,
             key: Map[Domain, Hashable]) -> Iterable[Group]:
    """
    Groups iterable elements based on given key.
    """
    groups = defaultdict(list)  # type: Mapping[Hashable, List[Domain]]
    for element in iterable:
        groups[key(element)].append(element)
    yield from groups.items()


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


def first(iterable: Iterable[Domain]) -> Domain:
    """
    Returns first element of iterable.
    """
    try:
        return next(iter(iterable))
    except StopIteration as error:
        raise ValueError('Argument supposed to be non-empty.') from error


def trailer(size: int) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from the end of iterable.
    Resulted iterable will have size not greater than given one.
    """
    return functools.partial(deque,
                             maxlen=size)


def last(iterable: Iterable[Domain]) -> Domain:
    """
    Returns last element of iterable.
    """
    try:
        return deque(iterable,
                     maxlen=1)[0]
    except IndexError as error:
        raise ValueError('Argument supposed to be non-empty.') from error


@singledispatch
def capacity(iterable: Iterable[Any]) -> int:
    return sum(1 for _ in iterable)


@capacity.register(abc.Sized)
def sized_capacity(iterable: Sized) -> int:
    return len(iterable)
