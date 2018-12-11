import functools
import itertools
from collections import abc
from contextlib import suppress
from operator import add
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Dict,
                    Iterable,
                    Optional,
                    Tuple,
                    Union)

from paradigm import signatures

from .hints import (Domain,
                    Intermediate,
                    Map,
                    Operator,
                    Range)


def identity(argument: Domain) -> Domain:
    """
    Returns object itself.
    """
    return argument


def compose(last_function: Map[Any, Range],
            *front_functions: Callable[..., Any]) -> Callable[..., Range]:
    """
    Returns functions composition.
    """

    def binary_compose(left_function: Map[Intermediate, Range],
                       right_function: Callable[..., Intermediate]
                       ) -> Callable[..., Range]:
        def composition(*args, **kwargs):
            return left_function(right_function(*args, **kwargs))

        return composition

    functions = (last_function,) + front_functions
    return functools.reduce(binary_compose, functions)


def combine(maps: Iterable[Map]) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies each map to corresponding argument.
    """

    def combined(arguments: Iterable[Domain]) -> Iterable[Range]:
        yield from (map_(argument)
                    for map_, argument in zip(maps, arguments))

    return combined


class ApplierBase(abc.Callable):
    def __init__(self, function: Callable[..., Range],
                 *args: Domain,
                 **kwargs: Domain) -> None:
        if isinstance(function, type(self)):
            args = function.args + args
            kwargs = {**function.keywords, **kwargs}
            function = function.func
        self.func = function
        self.args = args
        self.keywords = kwargs

    def __repr__(self) -> str:
        arguments_strings = itertools.chain(
                [repr(self.func)],
                arguments_to_strings(self.args, self.keywords))
        cls = type(self)
        return (cls.__module__ + '.' + cls.__qualname__
                + '(' + ', '.join(arguments_strings) + ')')


class Curry(ApplierBase):
    def __init__(self,
                 function: Callable[..., Range],
                 signature: signatures.Base,
                 *args: Domain,
                 **kwargs: Domain) -> None:
        super().__init__(function, *args, **kwargs)
        self.signature = signature

    def __call__(self, *args: Domain, **kwargs: Domain
                 ) -> Union['Curry', Range]:
        args = self.args + args
        kwargs = {**self.keywords, **kwargs}
        try:
            return self.func(*args, **kwargs)
        except TypeError:
            if not self.signature.has_unset_parameters(*args, **kwargs):
                raise
        return type(self)(self.func, self.signature, *args, **kwargs)


def arguments_to_strings(positional_arguments: Tuple[Any, ...],
                         keyword_arguments: Dict[str, Any]) -> Iterable[str]:
    yield from map(repr, positional_arguments)
    yield from itertools.starmap('{}={!r}'.format, keyword_arguments.items())


def curry(function: Callable[..., Range],
          *,
          signature: Optional[signatures.Base] = None) -> Curry:
    """
    Returns curried version of given function.
    """
    if signature is None:
        signature = signatures.factory(function)
    return Curry(function, signature)


def pack(function: Callable[..., Range]) -> Map[Iterable[Domain], Range]:
    """
    Returns function that works with single iterable parameter
    by unpacking elements to given function.
    """

    def packed(args: Iterable[Domain],
               kwargs: Dict[str, Any] = MappingProxyType({})) -> Range:
        return function(*args, **kwargs)

    members_factories = dict(members_copiers)
    members_factories['__name__'] = functools.partial(add, 'packed ')
    members_factories['__qualname__'] = functools.partial(add, 'packed ')
    update_metadata(function, packed,
                    members_factories=members_factories)
    return packed


def to_constant(object_: Domain) -> Callable[..., Domain]:
    """
    Returns function that returns given object.
    """

    def constant(*_: Domain, **__: Domain) -> Domain:
        return object_

    object_repr = repr(object_)
    constant.__name__ = object_repr + ' constant'
    constant.__qualname__ = object_repr + ' constant'
    constant.__doc__ = 'Returns {}.'.format(object_repr)
    return constant


def flip(function: Callable[..., Range]) -> Callable[..., Range]:
    """
    Returns function with positional arguments flipped.
    """

    def flipped(*args, **kwargs) -> Range:
        return function(*args[::-1], **kwargs)

    members_factories = dict(members_copiers)
    members_factories['__name__'] = functools.partial(add, 'flipped ')
    members_factories['__qualname__'] = functools.partial(add, 'flipped ')
    update_metadata(function, flipped,
                    members_factories=members_factories)
    return flipped


def cleave(functions: Iterable[Callable[..., Range]]
           ) -> Callable[..., Iterable[Range]]:
    """
    Returns function that separately applies
    given functions to the same arguments.
    """

    def cleft(*args, **kwargs) -> Range:
        yield from (function(*args, **kwargs)
                    for function in functions)

    return cleft


members_copiers = dict(itertools.chain(zip(functools.WRAPPER_ASSIGNMENTS,
                                           itertools.repeat(identity))))


def update_metadata(source_function: Callable[..., Range],
                    target_function: Callable[..., Range],
                    *,
                    members_factories: Dict[str, Operator]) -> None:
    for member_name, member_factory in members_factories.items():
        try:
            source_member = getattr(source_function, member_name)
        except AttributeError:
            continue
        else:
            target_member = member_factory(source_member)
            setattr(target_function, member_name, target_member)
    with suppress(AttributeError):
        target_function.__dict__.update(source_function.__dict__)
