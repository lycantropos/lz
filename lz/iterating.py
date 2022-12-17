import collections as _collections
import functools as _functools
import itertools as _itertools
import typing as _t
from operator import is_not as _is_not

from .functional import flatmap as _flatmap

_T1 = _t.TypeVar('_T1')
_T2 = _t.TypeVar('_T2')


@_functools.singledispatch
def capacity(_value: _t.Any) -> int:
    """
    Returns number of elements in value.

    >>> capacity(range(0))
    0
    >>> capacity(range(10))
    10
    """
    raise TypeError(type(_value))


@capacity.register(_collections.abc.Iterable)
def _(_iterable: _t.Iterable[_t.Any]) -> int:
    counter = _itertools.count()
    # order matters: if `counter` goes first,
    # then it will be incremented even for empty `iterable`
    _collections.deque(zip(_iterable, counter),
                       maxlen=0)
    return next(counter)


@capacity.register(_collections.abc.Collection)
def _(_iterable: _t.Sized) -> int:
    """
    Returns number of elements in sized iterable.
    """
    return len(_iterable)


def first(_iterable: _t.Iterable[_T1]) -> _T1:
    """
    Returns first element of iterable.

    >>> first(range(10))
    0
    """
    try:
        return next(iter(_iterable))
    except StopIteration as error:
        raise ValueError('Argument supposed to be non-empty.') from error


def last(_iterable: _t.Iterable[_T1]) -> _T1:
    """
    Returns last element of iterable.

    >>> last(range(10))
    9
    """
    try:
        return _collections.deque(_iterable,
                                  maxlen=1)[0]
    except IndexError as error:
        raise ValueError('Argument supposed to be non-empty.') from error


def cut(_iterable: _t.Iterable[_T1],
        *,
        slice_: slice) -> _t.Iterable[_T1]:
    """
    Selects elements from iterable based on given slice.

    Slice fields supposed to be unset or non-negative
    since it is hard to evaluate negative indices/step for arbitrary iterable
    which may be potentially infinite
    or change previous elements if iterating made backwards.
    """
    yield from _itertools.islice(_iterable,
                                 slice_.start, slice_.stop, slice_.step)


def cutter(_slice: slice) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]]:
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
    result = _functools.partial(cut,
                                slice_=_slice)
    result.__doc__ = ('Selects elements from iterable {slice}.'
                      .format(slice=_slice_to_description(_slice)))
    return result


def _slice_to_description(_slice: slice) -> str:
    """Generates human readable representation of `slice` object."""
    slice_description_parts = []
    start_is_specified = bool(_slice.start)
    if start_is_specified:
        slice_description_parts.append('starting from position {start}'
                                       .format(start=_slice.start))
    step_is_specified = _slice.step is not None
    if step_is_specified:
        slice_description_parts.append('with step {step}'
                                       .format(step=_slice.step))
    if _slice.stop is not None:
        stop_description_part = ('stopping at position {stop}'
                                 .format(stop=_slice.stop))
        if start_is_specified or step_is_specified:
            stop_description_part = 'and ' + stop_description_part
        slice_description_parts.append(stop_description_part)
    return ' '.join(slice_description_parts)


def chopper(
        _size: int
) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_t.Sequence[_T1]]]:
    """
    Returns function that splits iterable into chunks of given size.

    >>> in_three = chopper(3)
    >>> list(map(tuple, in_three(range(10))))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
    """
    return _functools.partial(chop,
                              size=_size)


@_functools.singledispatch
def chop(_iterable: _t.Iterable[_T1],
         *,
         size: int) -> _t.Iterable[_t.Sequence[_T1]]:
    """
    Splits iterable into chunks of given size.
    """
    iterator = iter(_iterable)
    yield from iter(lambda: tuple(_itertools.islice(iterator, size)), ())


@chop.register(_collections.abc.Sequence)
def _(_iterable: _t.Sequence[_T1],
      *,
      size: int) -> _t.Iterable[_t.Sequence[_T1]]:
    """
    Splits sequence into chunks of given size.
    """
    if not size:
        return
    for start in range(0, len(_iterable), size):
        yield _iterable[start:start + size]


# deque do not support slice notation
chop.register(_collections.deque, chop.registry[object])

in_two = chopper(2)
in_three = chopper(3)
in_four = chopper(4)


def slide(_iterable: _t.Iterable[_T1],
          *,
          size: int) -> _t.Iterable[_t.Tuple[_T1, ...]]:
    """
    Slides over iterable with window of given size.
    """
    iterator = iter(_iterable)
    initial = tuple(_itertools.islice(iterator, size))

    def shift(previous: _t.Tuple[_T1, ...],
              element: _T1) -> _t.Tuple[_T1, ...]:
        return previous[1:] + (element,)

    yield from _itertools.accumulate(
            _itertools.chain([initial], iterator),
            _t.cast(_t.Callable[[_t.Any, _t.Any], _t.Tuple[_T1, ...]], shift)
    )


def slider(_size: int) -> _t.Callable[[_t.Iterable[_T1]],
                                      _t.Iterable[_t.Tuple[_T1, ...]]]:
    """
    Returns function that slides over iterable with window of given size.

    >>> pairwise = slider(2)
    >>> list(pairwise(range(10)))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    """
    return _functools.partial(slide,
                              size=_size)


pairwise = slider(2)
triplewise = slider(3)
quadruplewise = slider(4)


def header(_size: int) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]]:
    """
    Returns function that selects elements from the beginning of iterable.
    Resulted iterable will have size not greater than given one.

    >>> to_first_pair = header(2)
    >>> list(to_first_pair(range(10)))
    [0, 1]
    """
    return cutter(slice(_size))


@_functools.singledispatch
def trail(_iterable: _t.Iterable[_T1],
          *,
          size: int) -> _t.Iterable[_T1]:
    """
    Selects elements from the end of iterable.
    Resulted iterable will have size not greater than given one.
    """
    return _collections.deque(_iterable,
                              maxlen=size)


@trail.register(_collections.abc.Sequence)
def _(iterable: _t.Sequence[_T1],
      *,
      size: int) -> _t.Sequence[_T1]:
    """
    Selects elements from the end of sequence.
    Resulted sequence will have size not greater than given one.
    """
    return iterable[-size:] if size else iterable[:size]


# deque do not support slice notation
trail.register(_collections.deque, trail.registry[object])


def trailer(_size: int) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T1]]:
    """
    Returns function that selects elements from the end of iterable.
    Resulted iterable will have size not greater than given one.

    >>> to_last_pair = trailer(2)
    >>> list(to_last_pair(range(10)))
    [8, 9]
    """
    return _functools.partial(trail,
                              size=_size)


def mapper(
        _map: _t.Callable[[_T1], _T2]
) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T2]]:
    """
    Returns function that applies given map to the each element of iterable.

    >>> to_str = mapper(str)
    >>> list(to_str(range(10)))
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    """
    return _t.cast(_t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T2]],
                   _functools.partial(map, _map))


def flatmapper(
        _map: _t.Callable[[_T1], _t.Iterable[_T2]]
) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T2]]:
    """
    Returns function that applies map to the each element of iterable
    and flattens results.

    >>> relay = flatmapper(range)
    >>> list(relay(range(5)))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3]
    """
    return _functools.partial(_flatmap, _map)


Group = _t.Tuple[_t.Hashable, _t.Iterable[_T1]]


def group_by(_iterable: _t.Iterable[_T1],
             *,
             key: _t.Callable[[_T1], _t.Hashable],
             mapping_cls: _t.Type[_t.MutableMapping]) -> _t.Iterable[Group]:
    """
    Groups iterable elements based on given key.
    """
    groups = mapping_cls()
    for element in _iterable:
        groups.setdefault(key(element), []).append(element)
    yield from groups.items()


def grouper(
        _key: _t.Callable[[_T1], _t.Hashable],
        *,
        mapping_cls: _t.Type[_t.MutableMapping] = _collections.OrderedDict
) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[Group]]:
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
    return _functools.partial(group_by,
                              key=_key,
                              mapping_cls=mapping_cls)


def expand(_value: _T1) -> _t.Iterable[_T1]:
    """
    Wraps value into iterable.

    >>> list(expand(0))
    [0]
    """
    yield _value


def flatten(_iterable: _t.Iterable[_t.Iterable[_T1]]) -> _t.Iterable[_T1]:
    """
    Returns plain iterable from iterable of iterables.

    >>> list(flatten([range(5), range(10, 20)]))
    [0, 1, 2, 3, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    """
    yield from _itertools.chain.from_iterable(_iterable)


def interleave(_iterable: _t.Iterable[_t.Iterable[_T1]]) -> _t.Iterable[_T1]:
    """
    Interleaves elements from given iterable of iterables.

    >>> list(interleave([range(5), range(10, 20)]))
    [0, 10, 1, 11, 2, 12, 3, 13, 4, 14, 15, 16, 17, 18, 19]
    """
    iterators = _itertools.cycle(_t.cast(_t.Iterable[_t.Iterator[_T1]],
                                         map(iter, _iterable)))
    while True:
        try:
            for iterator in iterators:
                yield next(iterator)
        except StopIteration:
            is_not_exhausted = _functools.partial(_is_not, iterator)
            iterators = _itertools.cycle(_itertools.takewhile(is_not_exhausted,
                                                              iterators))
        else:
            return
