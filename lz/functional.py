import functools
import operator
from typing import (Any,
                    Callable,
                    Iterable,
                    Tuple,
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


def combine(*maps: Map) -> Map[Tuple[Domain, ...],
                               Tuple[Range, ...]]:
    def combined(arguments: Tuple[Domain, ...]) -> Tuple[Range, ...]:
        if len(arguments) != len(maps):
            raise ValueError('There should be {count} arguments '
                             'for each of maps, '
                             'but found {actual_count}.'
                             .format(count=len(maps),
                                     actual_count=len(arguments)))
        return tuple(map_(argument)
                     for map_, argument in zip(maps, arguments))

    return combined


def unpack(function: Callable[..., Range]) -> Map[Iterable[Domain], Range]:
    @functools.wraps(function)
    def unpacked(iterable: Iterable[Domain]) -> Range:
        return function(*iterable)

    return unpacked


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
