import inspect
from itertools import (chain,
                       starmap)
from typing import (Callable,
                    Dict,
                    Tuple,
                    Union)

from . import signatures
from .hints import (Domain,
                    Range)


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
        arguments_strings = list(chain(map(str, self.args),
                                       starmap('{}={}'.format,
                                               self.kwargs.items())))
        if arguments_strings:
            result += (' with partially applied {arguments}'
                       .format(arguments=', '.join(arguments_strings)))
        result += '>'
        return result


def curry(callable_: Callable[..., Range]) -> Curry:
    """
    Returns curried version of given callable.
    """
    callable_, args, kwargs = unwrap(callable_)
    signature = signatures.factory(callable_)
    return Curry(callable_, signature, *args, **kwargs)


def unwrap(object_: Callable[..., Range]
           ) -> Tuple[Callable, Tuple[Domain, ...], Dict[str, Domain]]:
    try:
        return inspect.unwrap(object_.func), object_.args, object_.keywords
    except AttributeError:
        return inspect.unwrap(object_), (), {}
