import functools
import itertools
from typing import (Callable,
                    Iterable,
                    List,
                    Tuple)

from .hints import (Domain,
                    Map,
                    Range)
from .iterating import expand


def accumulator(function: Callable[[Range, Domain], Range],
                initial: Range
                ) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from left to right.

    >>> import math
    >>> to_pi_approximations = accumulator(round, math.pi)
    >>> list(to_pi_approximations(range(5, 0, -1)))
    [3.141592653589793, 3.14159, 3.1416, 3.142, 3.14, 3.1]
    """
    return functools.partial(accumulate,
                             function=function,
                             initial=initial)


def accumulate(iterable: Iterable[Domain],
               function: Callable[[Range, Domain], Range],
               initial: Range) -> Iterable[Range]:
    """
    Yields cumulative results of given binary function
    starting from given initial object in direction from left to right.
    """
    yield from itertools.accumulate(attach(iterable, initial), function)


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    """
    Returns function that prepends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [100, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return functools.partial(attach,
                             object_=object_)


@functools.singledispatch
def attach(iterable: Iterable[Domain],
           object_: Domain) -> Iterable[Domain]:
    """
    Prepends given object to the iterable.
    """
    yield from itertools.chain(expand(object_), iterable)


@attach.register(list)
def _(iterable: List[Domain],
      object_: Domain) -> List[Domain]:
    """
    Prepends given object to the list.
    """
    return [object_] + iterable


@attach.register(tuple)
def _(iterable: Tuple[Domain, ...],
      object_: Domain) -> Tuple[Domain, ...]:
    """
    Prepends given object to the tuple.
    """
    return (object_,) + iterable


def folder(function: Callable[[Range, Domain], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from left to right.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(range(1, 10))
    '(((((((((0 + 1) + 2) + 3) + 4) + 5) + 6) + 7) + 8) + 9)'
    """
    return functools.partial(fold,
                             function=function,
                             initial=initial)


def fold(iterable: Iterable[Domain],
         function: Callable[[Range, Domain], Range],
         initial: Range) -> Range:
    """
    Cumulatively applies given binary function
    starting from given initial object in direction from left to right.
    """
    return functools.reduce(function, iterable, initial)


Applier = functools.partial


def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the left end.

    >>> count_from_zero_to = applier(range, 0)
    >>> list(count_from_zero_to(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return Applier(function, *args, **kwargs)
