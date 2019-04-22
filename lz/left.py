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
    """
    return functools.partial(attach,
                             object_=object_)


@functools.singledispatch
def attach(iterable: Iterable[Domain],
           object_: Domain) -> Iterable[Domain]:
    yield from itertools.chain(expand(object_), iterable)


@attach.register(list)
def attach_to_list(iterable: List[Domain],
                   object_: Domain) -> List[Domain]:
    return [object_] + iterable


@attach.register(tuple)
def attach_to_tuple(iterable: Tuple[Domain, ...],
                    object_: Domain) -> Tuple[Domain, ...]:
    return (object_,) + iterable


def folder(function: Callable[[Range, Domain], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from left to right.
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
    """
    return Applier(function, *args, **kwargs)
