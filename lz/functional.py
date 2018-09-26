import functools
import itertools
import operator
from typing import (Any,
                    Callable,
                    Collection,
                    Iterable,
                    TypeVar)

from .hints import (Domain,
                    Map,
                    Predicate,
                    Range)


def identity(argument: Domain) -> Domain:
    return argument


def compose(*maps: Map) -> Map[Domain, Any]:
    Intermediate = TypeVar('Intermediate')

    def binary_compose(left_map: Map[Intermediate, Range],
                       right_map: Map[Domain, Intermediate]
                       ) -> Map[Domain, Range]:
        def composition(argument: Domain) -> Any:
            return left_map(right_map(argument))

        return composition

    return functools.reduce(binary_compose, maps)


def combine(*maps: Map) -> Map[Iterable[Domain], Iterable[Range]]:
    def chop(arguments: Iterable[Domain]) -> Collection[Domain]:
        return tuple(itertools.islice(arguments, len(maps)))

    def combined(arguments: Iterable[Domain]) -> Iterable[Range]:
        arguments = chop(arguments)
        if len(arguments) != len(maps):
            raise ValueError('There should be {count} arguments '
                             'for each of maps, '
                             'but found {actual_count}.'
                             .format(count=len(maps),
                                     actual_count=len(arguments)))
        yield from (map_(argument)
                    for map_, argument in zip(maps, arguments))

    return combined


def pack(function: Callable[..., Range]) -> Map[Iterable[Domain], Range]:
    """
    Creates function that works with single iterable parameter
    by propagating elements to a wrapped function.
    """
    @functools.wraps(function)
    def packed(iterable: Iterable[Domain]) -> Range:
        return function(*iterable)

    return packed


def to_constant(object_: Domain) -> Callable[..., Domain]:
    def constant(*_: Domain, **__: Domain) -> Domain:
        return object_

    return constant


def flip(function: Callable[..., Range]) -> Callable[..., Range]:
    @functools.wraps(function)
    def flipped(*args, **kwargs):
        return function(*reversed(args), **kwargs)

    return flipped


def negate(predicate: Predicate) -> Predicate:
    return compose(operator.not_, predicate)
