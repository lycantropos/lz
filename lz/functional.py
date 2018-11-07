import functools
import inspect
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
        self.kwargs = kwargs

    def __call__(self, *args: Domain, **kwargs: Domain
                 ) -> Union['Curry', Range]:
        args = self.args + args
        kwargs = {**self.kwargs, **kwargs}
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
                and self.kwargs == other.kwargs)

    def __repr__(self) -> str:
        result = ('<curried {callable_}'
                  .format(callable_=self.callable_))
        arguments_strings = list(
                itertools.chain(map(str, self.args),
                                itertools.starmap('{}={}'.format,
                                                  self.kwargs.items())))
        if arguments_strings:
            result += (' with partially applied {arguments}'
                       .format(arguments=', '.join(arguments_strings)))
        result += '>'
        return result


def unwrap(function: Callable[..., Range]) -> Tuple[Callable[..., Range],
                                                    Tuple[Domain, ...],
                                                    Dict[str, Domain]]:
    original_function = function
    try:
        function, args, kwargs = (inspect.unwrap(function.func),
                                  function.args,
                                  function.keywords)
    except AttributeError:
        return inspect.unwrap(original_function), (), {}
    else:
        if (not isinstance(function, Callable)
                or not isinstance(args, Iterable)
                or not isinstance(kwargs, Mapping)):
            return inspect.unwrap(original_function), (), {}
        return function, args, kwargs


def curry(callable_: Callable[..., Range]) -> Curry:
    """
    Returns curried version of given callable.
    """
    callable_, args, kwargs = unwrap(callable_)
    signature = signatures.factory(callable_)
    return Curry(callable_, signature, *args, **kwargs)


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


@functools.singledispatch
def flip(object_: Callable[..., Range]) -> Callable[..., Range]:
    """
    Returns function with positional arguments flipped.
    """

    @functools.wraps(object_)
    def flipped(*args, **kwargs) -> Range:
        return object_(*reversed(args), **kwargs)

    return flipped


@flip.register(functools.partial)
def flip_partial(object_: functools.partial) -> Callable[..., Range]:
    return functools.partial(flip(object_.func),
                             *object_.args,
                             **object_.keywords)


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
