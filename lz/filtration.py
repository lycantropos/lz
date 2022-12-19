import functools as _functools
import itertools as _itertools
import typing as _t
from collections import deque as _deque

from .replication import duplicate as _duplicate

_T = _t.TypeVar('_T')


def sift(_predicate: _t.Callable[[_T], bool],
         _value: _t.Iterable[_T]) -> _t.Iterable[_T]:
    """
    Selects elements from iterable which satisfy given predicate.

    >>> list(sift(bool, range(10)))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> list(sift(is_even, range(10)))
    [0, 2, 4, 6, 8]
    """
    return filter(_predicate, _value)


def sifter(
        _predicate: _t.Callable[[_T], bool]
) -> _t.Callable[[_t.Iterable[_T]], _t.Iterable[_T]]:
    """
    Returns function that selects elements from iterable
    which satisfy given predicate.

    >>> to_true_like = sifter(bool)
    >>> list(to_true_like(range(10)))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> to_even = sifter(is_even)
    >>> list(to_even(range(10)))
    [0, 2, 4, 6, 8]
    """
    return _functools.partial(sift, _predicate)


def scavenge(_predicate: _t.Callable[[_T], bool],
             _value: _t.Iterable[_T]) -> _t.Iterable[_T]:
    """
    Selects elements from iterable which dissatisfy given predicate.

    >>> list(scavenge(bool, range(10)))
    [0]

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> list(scavenge(is_even, range(10)))
    [1, 3, 5, 7, 9]
    """
    return _itertools.filterfalse(_predicate, _value)


def scavenger(
        _predicate: _t.Callable[[_T], bool]
) -> _t.Callable[[_t.Iterable[_T]], _t.Iterable[_T]]:
    """
    Returns function that selects elements from iterable
    which dissatisfy given predicate.

    >>> to_false_like = scavenger(bool)
    >>> list(to_false_like(range(10)))
    [0]

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> to_odd = scavenger(is_even)
    >>> list(to_odd(range(10)))
    [1, 3, 5, 7, 9]
    """
    return _functools.partial(scavenge, _predicate)


def separate(
        _predicate: _t.Callable[[_T], bool], _value: _t.Iterable[_T]
) -> _t.Tuple[_t.Iterable[_T], _t.Iterable[_T]]:
    """
    Returns pair of iterables
    first of which consists of elements that dissatisfy given predicate
    and second one consists of elements that satisfy given predicate.

    >>> tuple(map(list, separate(bool, range(10))))
    ([0], [1, 2, 3, 4, 5, 6, 7, 8, 9])

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> tuple(map(list, separate(is_even, range(10))))
    ([1, 3, 5, 7, 9], [0, 2, 4, 6, 8])
    """
    iterator = iter(_value)
    unsatisfying: _t.Deque[_T] = _deque()
    satisfying: _t.Deque[_T] = _deque()

    def fill(queue: _t.Deque[_T]) -> _t.Iterable[_T]:
        while True:
            while not queue:
                try:
                    element = next(iterator)
                except StopIteration:
                    return
                subject, element = _duplicate(element)
                (satisfying
                 if _predicate(subject)
                 else unsatisfying).append(element)
            yield queue.popleft()

    return fill(unsatisfying), fill(satisfying)


def separator(
        _predicate: _t.Callable[[_T], bool]
) -> _t.Callable[[_t.Iterable[_T]],
                 _t.Tuple[_t.Iterable[_T], _t.Iterable[_T]]]:
    """
    Returns function that returns pair of iterables
    first of which consists of elements that dissatisfy given predicate
    and second one consists of elements that satisfy given predicate.

    >>> split_by_truth = separator(bool)
    >>> tuple(map(list, split_by_truth(range(10))))
    ([0], [1, 2, 3, 4, 5, 6, 7, 8, 9])

    >>> def is_even(number: int) -> bool:
    ...     return number % 2 == 0
    >>> split_by_evenness = separator(is_even)
    >>> tuple(map(list, split_by_evenness(range(10))))
    ([1, 3, 5, 7, 9], [0, 2, 4, 6, 8])
    """
    return _functools.partial(separate, _predicate)


def grab(_predicate: _t.Callable[[_T], bool],
         _value: _t.Iterable[_T]) -> _t.Iterable[_T]:
    """
    Selects elements from the beginning of iterable
    while given predicate is satisfied.

    >>> grab_while_true_like = grabber(bool)
    >>> list(grab_while_true_like(range(10)))
    []

    >>> from operator import gt
    >>> from functools import partial
    >>> grab_while_less_than_five = grabber(partial(gt, 5))
    >>> list(grab_while_less_than_five(range(10)))
    [0, 1, 2, 3, 4]
    """
    return _itertools.takewhile(_predicate, _value)


def grabber(
        _predicate: _t.Callable[[_T], bool]
) -> _t.Callable[[_t.Iterable[_T]], _t.Iterable[_T]]:
    """
    Returns function that selects elements from the beginning of iterable
    while given predicate is satisfied.

    >>> grab_while_true_like = grabber(bool)
    >>> list(grab_while_true_like(range(10)))
    []

    >>> from operator import gt
    >>> from functools import partial
    >>> grab_while_less_than_five = grabber(partial(gt, 5))
    >>> list(grab_while_less_than_five(range(10)))
    [0, 1, 2, 3, 4]
    """
    return _functools.partial(grab, _predicate)


def kick(_predicate: _t.Callable[[_T], bool],
         _value: _t.Iterable[_T]) -> _t.Iterable[_T]:
    """
    Skips elements from the beginning of iterable
    while given predicate is satisfied.

    >>> list(kick(bool, range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> from operator import gt
    >>> from functools import partial
    >>> list(kick(partial(gt, 5), range(10)))
    [5, 6, 7, 8, 9]
    """
    return _itertools.dropwhile(_predicate, _value)


def kicker(
        _predicate: _t.Callable[[_T], bool]
) -> _t.Callable[[_t.Iterable[_T]], _t.Iterable[_T]]:
    """
    Returns function that skips elements from the beginning of iterable
    while given predicate is satisfied.

    >>> kick_while_true_like = kicker(bool)
    >>> list(kick_while_true_like(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> from operator import gt
    >>> from functools import partial
    >>> kick_while_less_than_five = kicker(partial(gt, 5))
    >>> list(kick_while_less_than_five(range(10)))
    [5, 6, 7, 8, 9]
    """
    return _functools.partial(kick, _predicate)
