import functools
import itertools
from collections import (OrderedDict,
                         abc,
                         deque)
from operator import is_not
from typing import (Any,
                    Hashable,
                    Iterable,
                    MutableMapping,
                    Sequence,
                    Sized,
                    Tuple,
                    Type)

from .functional import flatmap
from .hints import (Domain,
                    Map,
                    Operator,
                    Range)


@functools.singledispatch
def capacity(iterable: Iterable[Any]) -> int:
    """
    Returns number of elements in iterable.

    >>> capacity(range(0))
    0
    >>> capacity(range(10))
    10
    """
    counter = itertools.count()
    # order matters: if `counter` goes first,
    # then it will be incremented even for empty `iterable`
    deque(zip(iterable, counter),
          maxlen=0)
    return next(counter)


@capacity.register(abc.Sized)
def _(iterable: Sized) -> int:
    """
    Returns number of elements in sized iterable.
    """
    return len(iterable)


def first(iterable: Iterable[Domain]) -> Domain:
    """
    Returns first element of iterable.

    >>> first(range(10))
    0
    """
    try:
        return next(iter(iterable))
    except StopIteration as error:
        raise ValueError('Argument supposed to be non-empty.') from error


def last(iterable: Iterable[Domain]) -> Domain:
    """
    Returns last element of iterable.

    >>> last(range(10))
    9
    """
    try:
        return deque(iterable,
                     maxlen=1)[0]
    except IndexError as error:
        raise ValueError('Argument supposed to be non-empty.') from error


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


def cutter(slice_: slice) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from iterable based on given slice.

    >>> to_first_triplet = cutter(slice(3))
    >>> list(to_first_triplet(range(10)))
    [0, 1, 2]

    >>> to_second_triplet = cutter(slice(3, 6))
    >>> list(to_second_triplet(range(10)))
    [3, 4, 5]

    >>> cut_out_every_third = cutter(slice(0, None, 3))
    >>> list(cut_out_every_third(range(10)))
    [0, 3, 6, 9]
    """
    result = functools.partial(cut,
                               slice_=slice_)
    result.__doc__ = ('Selects elements from iterable {slice}.'
                      .format(slice=_slice_to_description(slice_)))
    return result


def _slice_to_description(slice_: slice) -> str:
    """Generates human readable representation of `slice` object."""
    slice_description_parts = []
    start_is_specified = bool(slice_.start)
    if start_is_specified:
        slice_description_parts.append('starting from position {start}'
                                       .format(start=slice_.start))
    step_is_specified = slice_.step is not None
    if step_is_specified:
        slice_description_parts.append('with step {step}'
                                       .format(step=slice_.step))
    if slice_.stop is not None:
        stop_description_part = ('stopping at position {stop}'
                                 .format(stop=slice_.stop))
        if start_is_specified or step_is_specified:
            stop_description_part = 'and ' + stop_description_part
        slice_description_parts.append(stop_description_part)
    return ' '.join(slice_description_parts)


def chopper(size: int) -> Map[Iterable[Domain], Iterable[Sequence[Domain]]]:
    """
    Returns function that splits iterable into chunks of given size.

    >>> in_three = chopper(3)
    >>> list(map(tuple, in_three(range(10))))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
    """
    result = functools.partial(chop,
                               size=size)
    result.__doc__ = ('Splits iterable into chunks of size {size}.\n'
                      .format(size=size))
    return result


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
def _(iterable: Sequence[Domain],
      *,
      size: int) -> Iterable[Sequence[Domain]]:
    """
    Splits sequence into chunks of given size.
    """
    if not size:
        return
    for start in range(0, len(iterable), size):
        yield iterable[start:start + size]


# deque do not support slice notation
chop.register(deque, chop.registry[object])

in_two = chopper(2)
in_three = chopper(3)
in_four = chopper(4)


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


def slider(size: int) -> Map[Iterable[Domain], Iterable[Tuple[Domain, ...]]]:
    """
    Returns function that slides over iterable with window of given size.

    >>> pairwise = slider(2)
    >>> list(pairwise(range(10)))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    """
    result = functools.partial(slide,
                               size=size)
    result.__doc__ = ('Slides over iterable with window of size {size}.'
                      .format(size=size))
    return result


pairwise = slider(2)
triplewise = slider(3)
quadruplewise = slider(4)


def header(size: int) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from the beginning of iterable.
    Resulted iterable will have size not greater than given one.

    >>> to_first_pair = header(2)
    >>> list(to_first_pair(range(10)))
    [0, 1]
    """
    result = cutter(slice(size))
    result.__doc__ = ('Selects {size} elements from the beginning of iterable.'
                      .format(size=size))
    return result


@functools.singledispatch
def trail(iterable: Iterable[Domain],
          *,
          size: int) -> Iterable[Domain]:
    """
    Selects elements from the end of iterable.
    Resulted iterable will have size not greater than given one.
    """
    return deque(iterable,
                 maxlen=size)


@trail.register(abc.Sequence)
def _(iterable: Sequence[Domain],
      *,
      size: int) -> Sequence[Domain]:
    """
    Selects elements from the end of sequence.
    Resulted sequence will have size not greater than given one.
    """
    return iterable[-size:] if size else iterable[:size]


# deque do not support slice notation
trail.register(deque, trail.registry[object])


def trailer(size: int) -> Operator[Iterable[Domain]]:
    """
    Returns function that selects elements from the end of iterable.
    Resulted iterable will have size not greater than given one.

    >>> to_last_pair = trailer(2)
    >>> list(to_last_pair(range(10)))
    [8, 9]
    """
    result = functools.partial(trail,
                               size=size)
    result.__doc__ = ('Selects {size} elements from the end of iterable.'
                      .format(size=size))
    return result


def mapper(map_: Map) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies given map to the each element of iterable.

    >>> to_str = mapper(str)
    >>> list(to_str(range(10)))
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    """
    return functools.partial(map, map_)


def flatmapper(map_: Map[Domain, Iterable[Range]]
               ) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies map to the each element of iterable
    and flattens results.

    >>> relay = flatmapper(range)
    >>> list(relay(range(5)))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3]
    """
    return functools.partial(flatmap, map_)


Group = Tuple[Hashable, Iterable[Domain]]


def group_by(iterable: Iterable[Domain],
             *,
             key: Map[Domain, Hashable],
             mapping_cls: Type[MutableMapping]) -> Iterable[Group]:
    """
    Groups iterable elements based on given key.
    """
    groups = mapping_cls()
    for element in iterable:
        groups.setdefault(key(element), []).append(element)
    yield from groups.items()


def grouper(key: Map[Domain, Hashable],
            *,
            mapping_cls: Type[MutableMapping] = OrderedDict
            ) -> Map[Iterable[Domain], Iterable[Group]]:
    """
    Returns function that groups iterable elements based on given key.

    >>> group_by_absolute_value = grouper(abs)
    >>> list(group_by_absolute_value(range(-5, 5)))
    [(5, [-5]), (4, [-4, 4]), (3, [-3, 3]), (2, [-2, 2]), (1, [-1, 1]), (0, [0])]

    >>> def modulo_two(number: int) -> int:
    ...     return number % 2
    >>> group_by_evenness = grouper(modulo_two)
    >>> list(group_by_evenness(range(10)))
    [(0, [0, 2, 4, 6, 8]), (1, [1, 3, 5, 7, 9])]
    """
    return functools.partial(group_by,
                             key=key,
                             mapping_cls=mapping_cls)


def expand(object_: Domain) -> Iterable[Domain]:
    """
    Wraps object into iterable.

    >>> list(expand(0))
    [0]
    """
    yield object_


def flatten(iterable: Iterable[Iterable[Domain]]) -> Iterable[Domain]:
    """
    Returns plain iterable from iterable of iterables.

    >>> list(flatten([range(5), range(10, 20)]))
    [0, 1, 2, 3, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    """
    yield from itertools.chain.from_iterable(iterable)


def interleave(iterable: Iterable[Iterable[Domain]]) -> Iterable[Domain]:
    """
    Interleaves elements from given iterable of iterables.

    >>> list(interleave([range(5), range(10, 20)]))
    [0, 10, 1, 11, 2, 12, 3, 13, 4, 14, 15, 16, 17, 18, 19]
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
