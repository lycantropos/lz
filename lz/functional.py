import functools
import itertools
import operator
from typing import (Any,
                    Callable,
                    Iterable,
                    Tuple)

from .hints import (Domain,
                    Intermediate,
                    Map,
                    Predicate,
                    Range)


def identity(argument: Domain) -> Domain:
    return argument


def compose(last_function: Map[Any, Range],
            *front_functions: Callable[..., Any]) -> Callable[..., Range]:
    def binary_compose(left_function: Map[Intermediate, Range],
                       right_function: Callable[..., Intermediate]
                       ) -> Callable[..., Range]:
        def composition(*args, **kwargs):
            return left_function(right_function(*args, **kwargs))

        return composition

    functions = (last_function,) + front_functions
    return functools.reduce(binary_compose, functions)


def combine(maps: Iterable[Map]) -> Map[Iterable[Domain], Iterable[Range]]:
    def combined(arguments: Iterable[Domain]) -> Iterable[Range]:
        yield from (map_(argument)
                    for map_, argument in zip(maps, arguments))

    return combined


def pack(function: Callable[..., Range]) -> Map[Iterable[Domain], Range]:
    """
    Creates function that works with single iterable parameter
    by unpacking elements to original function.
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
