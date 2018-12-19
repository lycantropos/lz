import functools
import io
import itertools
import os
import sys
from collections import (abc,
                         defaultdict,
                         deque)
from operator import (is_not,
                      methodcaller,
                      sub)
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
from .functional import (combine,
                         compose)
from .hints import (Domain,
                    Map,
                    Operator,
                    Predicate,
                    Range,
                    Sortable)
from .replication import duplicate
from .textual import (decoder,
                      read_batch_from_end,
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
            batch_size: Optional[int] = ...,
            lines_separator: Optional[AnyStr] = ...,
            keep_lines_separator: bool = ...) -> Iterable[AnyStr]:
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
                 lines_separator: Optional[str] = None,
                 keep_lines_separator: bool = True) -> Iterable[str]:
    encoding = iterable.encoding
    if lines_separator is not None:
        lines_separator = lines_separator.encode(encoding)
    yield from map(decoder(encoding),
                   reverse(iterable.buffer,
                           batch_size=batch_size,
                           lines_separator=lines_separator,
                           keep_lines_separator=keep_lines_separator))


@reverse.register(io.BufferedReader)
@reverse.register(io.BytesIO)
def reverse_binary_stream(iterable: BinaryIO,
                          *,
                          batch_size: Optional[int] = None,
                          lines_separator: Optional[bytes] = None,
                          keep_lines_separator: bool = True
                          ) -> Iterable[bytes]:
    if lines_separator is None:
        lines_separator = (b'\r', b'\n', b'\r\n')
        lines_splitter = methodcaller(str.splitlines.__name__,
                                      keep_lines_separator)
    else:
        lines_splitter = functools.partial(split,
                                           separator=lines_separator,
                                           keep_separator=keep_lines_separator)
    stream_size = iterable.seek(0, os.SEEK_END)
    if batch_size is None:
        batch_size = stream_size or 1
    batches_count = ceil_division(stream_size, batch_size)
    remaining_bytes_indicator = itertools.islice(
            itertools.accumulate(itertools.chain([stream_size],
                                                 itertools.repeat(batch_size)),
                                 sub),
            batches_count)
    try:
        remaining_bytes_count = next(remaining_bytes_indicator)
    except StopIteration:
        return
    batch = read_batch_from_end(iterable,
                                size=batch_size,
                                end_position=remaining_bytes_count)
    segment, *lines = lines_splitter(batch)
    yield from reverse(lines)
    for remaining_bytes_count in remaining_bytes_indicator:
        batch = read_batch_from_end(iterable,
                                    size=batch_size,
                                    end_position=remaining_bytes_count)
        lines = lines_splitter(batch)
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


def interleave(iterable: Iterable[Iterable[Domain]]) -> Iterable[Domain]:
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


def flatmapper(map_: Map[Domain, Iterable[Range]]
               ) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies map to the each element of iterable
    and flattens results.
    """
    return compose(flatten, mapper(map_))


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
