import functools
import io
import itertools
import os
import sys
from collections import (abc,
                         defaultdict,
                         deque)
from operator import sub
from typing import (Any,
                    AnyStr,
                    BinaryIO,
                    Hashable,
                    IO,
                    Iterable,
                    Iterator,
                    List,
                    Mapping,
                    Optional,
                    Sequence,
                    TextIO,
                    Tuple,
                    overload)

from .arithmetical import ceil_division
from .functional import (cleave,
                         combine,
                         compose)
from .hints import (Domain,
                    Map,
                    Operator,
                    Predicate,
                    Range,
                    Sortable)
from .textual import (decoder,
                      read_batch,
                      split)


def mapper(map_: Map) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies given map to the each element of iterable.
    """
    return functools.partial(map, map_)


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
                   copier(2))


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


def chopper(size: int) -> Map[Iterable[Domain], Iterable[Tuple[Domain, ...]]]:
    """
    Returns function that splits iterable into chunks of given size.
    """
    cut = compose(tuple, cutter(slice(size)))
    return compose(grabber(),
                   cleave(itertools.repeat(cut)),
                   iter)


def slider(size: int) -> Map[Iterable[Domain], Iterable[Tuple[Domain, ...]]]:
    """
    Returns function that slides over iterable with window of given size.
    """

    def slide(iterable: Iterable[Domain]) -> Iterable[Tuple[Domain, ...]]:
        iterator = iter(iterable)
        result = tuple(itertools.islice(iterator, size))

        def shift(previous: Tuple[Domain, ...],
                  element: Domain) -> Tuple[Domain, ...]:
            return previous[1:] + (element,)

        yield from itertools.accumulate(itertools.chain([result], iterator),
                                        shift)

    return slide


def sorter(key: Map[Domain, Sortable] = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that generates sorted iterable by given key.
    """

    def sort(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from sorted(iterable,
                          key=key)

    return sort


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


@overload
def reverse(iterable: Iterator[Domain]) -> Iterable[Domain]:
    pass


@overload
def reverse(iterable: Sequence[Domain]) -> Iterable[Domain]:
    pass


@overload
def reverse(iterable: IO[AnyStr],
            *,
            batch_size: Optional[int] = None,
            lines_separator: AnyStr = '\n',
            keep_lines_separator: bool = True) -> Iterable[AnyStr]:
    pass


if sys.version_info >= (3, 6):
    from typing import Reversible


    @overload
    def reverse(iterable: Reversible[Domain]) -> Iterable[Domain]:
        pass


@overload
def reverse(iterable: Iterable[Domain]) -> Iterable[Domain]:
    pass


@functools.singledispatch
def reverse(object_: Iterable[Domain],
            **_: Any) -> Iterable[Domain]:
    """
    Returns iterable with reversed elements order.
    """
    raise TypeError('Unsupported iterable type: {type}.'
                    .format(type=type(object_)))


@reverse.register(abc.Iterator)
def reverse_iterator(iterable: Iterator[Domain]) -> Iterable[Domain]:
    yield from reversed(list(iterable))


@reverse.register(abc.Sequence)
def reverse_sequence(iterable: Sequence[Domain]) -> Iterable[Domain]:
    return iterable[::-1]


if sys.version_info >= (3, 6):
    from typing import Reversible


    @reverse.register(abc.Reversible)
    def reverse_reversible(iterable: Reversible[Domain]) -> Iterable[Domain]:
        yield from reversed(iterable)


@reverse.register(io.TextIOWrapper)
def reverse_file(iterable: TextIO,
                 *,
                 batch_size: Optional[int] = None,
                 lines_separator: str = '\n',
                 keep_lines_separator: bool = True) -> Iterable[str]:
    encoding = iterable.encoding
    yield from map(decoder(encoding),
                   reverse(iterable.buffer,
                           batch_size=batch_size,
                           lines_separator=lines_separator.encode(encoding),
                           keep_lines_separator=keep_lines_separator))


@reverse.register(io.BufferedReader)
def reverse_binary_file(iterable: BinaryIO,
                        *,
                        batch_size: Optional[int] = None,
                        lines_separator: bytes = b'\n',
                        keep_lines_separator: bool = True) -> Iterable[bytes]:
    file_size = iterable.seek(0, os.SEEK_END)
    if batch_size is None:
        batch_size = file_size
    batches_count = ceil_division(file_size, batch_size)
    remaining_bytes_indicator = itertools.islice(
            itertools.accumulate(itertools.chain([file_size],
                                                 itertools.repeat(batch_size)),
                                 sub),
            batches_count)
    remaining_bytes_count = next(remaining_bytes_indicator)
    batch = read_batch(iterable,
                       batch_size=batch_size,
                       remaining_bytes_count=remaining_bytes_count)
    segment, *lines = split(batch,
                            separator=lines_separator,
                            keep_separator=keep_lines_separator)
    yield from reverse(lines)
    for remaining_bytes_count in remaining_bytes_indicator:
        batch = read_batch(iterable,
                           batch_size=batch_size,
                           remaining_bytes_count=remaining_bytes_count)
        lines = split(batch,
                      separator=lines_separator,
                      keep_separator=keep_lines_separator)
        if batch.endswith(lines_separator):
            yield segment
        else:
            lines[-1] += segment
        segment, *lines = lines
        yield from reverse(lines)
    yield segment


def expand(object_: Domain) -> Iterable[Domain]:
    """
    Wraps object into iterable.
    """
    yield object_


def flatten(iterable: Iterable[Iterable[Domain]]) -> Iterable[Domain]:
    """
    Returns plain iterable from iterable of iterables.
    """
    yield from itertools.chain.from_iterable(iterable)


def flatmapper(map_: Map[Domain, Iterable[Range]]
               ) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies map to the each element of iterable
    and flattens results.
    """
    return compose(flatten, mapper(map_))


def copier(count: int) -> Map[Iterable[Domain], Iterable[Iterable[Domain]]]:
    """
    Returns function that creates independent copies of iterable.
    """
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


last = compose(first, trailer(1))
last.__doc__ = 'Returns last element of iterable.'
