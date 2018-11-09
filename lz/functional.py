import functools
import itertools
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Dict,
                    Iterable,
                    Mapping,
                    Tuple,
                    Union)

from paradigm import signatures

from .hints import (Domain,
                    Intermediate,
                    Map,
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


class Curry:
    def __init__(self,
                 callable_: Callable[..., Range],
                 signature: signatures.Base,
                 *args: Domain,
                 **kwargs: Domain) -> None:
        self.callable_ = callable_
        self.signature = signature
        self.args = args
        self.keywords = kwargs

    def __call__(self, *args: Domain, **kwargs: Domain
                 ) -> Union['Curry', Range]:
        args = self.args + args
        kwargs = {**self.keywords, **kwargs}
        try:
            return self.callable_(*args, **kwargs)
        except TypeError:
            if not self.signature.has_unset_parameters(*args, **kwargs):
                raise
            return type(self)(self.callable_, self.signature, *args, **kwargs)

    def __eq__(self, other: 'Curry') -> bool:
        if not isinstance(other, Curry):
            return NotImplemented
        return (self.callable_ is other.callable_
                and self.signature == other.signature
                and self.args == other.args
                and self.keywords == other.keywords)

    def __repr__(self) -> str:
        result = ('<curried {callable_}'
                  .format(callable_=self.callable_))
        arguments_strings = list(arguments_to_strings(self.args,
                                                      self.keywords))
        if arguments_strings:
            result += (' with partially applied {arguments}'
                       .format(arguments=', '.join(arguments_strings)))
        result += '>'
        return result


def handle_partial(function_factory: Callable[..., Callable[..., Range]]
                   ) -> Callable[..., Callable[..., Range]]:
    @functools.wraps(function_factory)
    def handled(function: Callable[..., Range], *args, **kwargs
                ) -> Callable[..., Range]:
        original_function = function
        try:
            function, applied_args, applied_kwargs = (function.func,
                                                      function.args,
                                                      function.keywords)
        except AttributeError:
            return function_factory(original_function, *args, **kwargs)
        else:
            if (not isinstance(function, Callable)
                    or not isinstance(applied_args, Iterable)
                    or not isinstance(applied_kwargs, Mapping)):
                return function_factory(original_function, *args, **kwargs)
        result = function_factory(function, *args, **kwargs)
        result.func = function
        try:
            result.args += applied_args
        except AttributeError:
            result.args = applied_args
        try:
            result.keywords = {**applied_kwargs, **result.keywords}
        except AttributeError:
            result.keywords = applied_kwargs
        return result

    return handled


def arguments_to_strings(args: Tuple[Any, ...], kwargs: Dict[str, Any]
                         ) -> Iterable[str]:
    yield from map(str, args)
    yield from itertools.starmap('{}={}'.format, kwargs.items())


@handle_partial
def curry(callable_: Callable[..., Range]) -> Curry:
    """
    Returns curried version of given callable.
    """
    signature = signatures.factory(callable_)
    return Curry(callable_, signature)


@handle_partial
def pack(function: Callable[..., Range]) -> Map[Iterable[Domain], Range]:
    """
    Returns function that works with single iterable parameter
    by unpacking elements to given function.
    """

    @functools.wraps(function)
    def packed(args: Iterable[Domain],
               kwargs: Dict[str, Any] = MappingProxyType({})) -> Range:
        return function(*args, **kwargs)

    return packed


def to_constant(object_: Domain) -> Callable[..., Domain]:
    """
    Returns function that returns given object.
    """

    def constant(*_: Domain, **__: Domain) -> Domain:
        return object_

    return constant


@handle_partial
def flip(function: Callable[..., Range]) -> Callable[..., Range]:
    """
    Returns function with positional arguments flipped.
    """

    @functools.wraps(function)
    def flipped(*args, **kwargs) -> Range:
        return function(*reversed(args), **kwargs)

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
