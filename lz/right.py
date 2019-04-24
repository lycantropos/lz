import functools
import itertools
from operator import (attrgetter,
                      methodcaller)
from typing import (Callable,
                    Iterable,
                    List,
                    Tuple)

from paradigm import signatures
from reprit import seekers
from reprit.base import generate_repr

from . import left
from .functional import (ApplierBase,
                         compose,
                         flip)
from .hints import (Domain,
                    Map,
                    Range)
from .iterating import expand
from .reversal import reverse


def accumulator(function: Callable[[Domain, Range], Range],
                initial: Range
                ) -> Map[Iterable[Domain], Iterable[Iterable[Range]]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from right to left.
    """
    left_accumulator = left.accumulator(flip(function), initial)
    return compose(left_accumulator, reverse)


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    """
    Returns function that appends given object to iterable.
    """
    return functools.partial(attach,
                             object_=object_)


@functools.singledispatch
def attach(iterable: Iterable[Domain],
           object_: Domain) -> Iterable[Domain]:
    yield from itertools.chain(iterable, expand(object_))


@attach.register(list)
def attach_to_list(iterable: List[Domain],
                   object_: Domain) -> List[Domain]:
    return iterable + [object_]


@attach.register(tuple)
def attach_to_tuple(iterable: Tuple[Domain, ...],
                    object_: Domain) -> Tuple[Domain, ...]:
    return iterable + (object_,)


def folder(function: Callable[[Domain, Range], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from right to left.
    """
    left_folder = left.folder(flip(function), initial)
    return compose(left_folder, reverse)


class Applier(ApplierBase):
    def __init__(self, function: Callable[..., Range],
                 *args: Domain,
                 **kwargs: Domain) -> None:
        super().__init__(function, *args, **kwargs)

    def __call__(self, *args: Domain, **kwargs: Domain) -> Range:
        return self.func(*args, *self.args, **self.keywords, **kwargs)

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)


@signatures.factory.register(Applier)
def _(object_: Applier) -> signatures.Base:
    return _bind_positionals(signatures.factory(object_.func)
                             .bind(**object_.keywords),
                             object_.args)


@functools.singledispatch
def _bind_positionals(signature: signatures.Base,
                      args: Tuple[Domain, ...]) -> signatures.Base:
    raise TypeError('Unsupported signature type: {type}.'
                    .format(type=type(signature)))


@_bind_positionals.register(signatures.Plain)
def _(signature: signatures.Plain,
      args: Tuple[Domain, ...]) -> signatures.Base:
    if not args:
        return signature
    variadic_positionals = signature.parameters_by_kind[
        signatures.Parameter.Kind.VARIADIC_POSITIONAL]
    positionals = (signature.parameters_by_kind[
                       signatures.Parameter.Kind.POSITIONAL_ONLY]
                   + signature.parameters_by_kind[
                       signatures.Parameter.Kind.POSITIONAL_OR_KEYWORD])
    if len(args) > len(positionals) and not variadic_positionals:
        value = 'argument' + 's' * (len(positionals) != 1)
        raise TypeError('Takes {parameters_count} positional {value}, '
                        'but {arguments_count} {verb} given.'
                        .format(parameters_count=len(positionals),
                                value=value,
                                arguments_count=len(args),
                                verb='was' if len(args) == 1 else 'were'))
    non_positionals = (signature.parameters_by_kind[
                           signatures.Parameter.Kind.KEYWORD_ONLY]
                       + signature.parameters_by_kind[
                           signatures.Parameter.Kind.VARIADIC_KEYWORD])
    signatures_parameters = []
    if len(args) <= len(positionals):
        signatures_parameters.append(positionals[:-len(args)]
                                     + non_positionals)
    if variadic_positionals:
        signatures_parameters.append(signature.parameters)
        for limit in range(1, len(args)):
            signatures_parameters.append(positionals[:-limit]
                                         + variadic_positionals
                                         + non_positionals)
    positionals_or_keywords = signature.parameters_by_kind[
        signatures.Parameter.Kind.POSITIONAL_OR_KEYWORD]
    positionals_or_keywords_with_defaults_count = sum(
            map(attrgetter('has_default'), positionals_or_keywords))
    for offset in range(1, positionals_or_keywords_with_defaults_count + 1):
        signatures_parameters.append(
                positionals[:-(len(args) + offset)]
                + [signatures.Parameter(
                        name=parameter.name,
                        kind=signatures.Parameter.Kind.KEYWORD_ONLY,
                        has_default=parameter.has_default)
                    for parameter in positionals_or_keywords[-offset:]]
                + non_positionals)
    return signatures.Overloaded(*(signatures.Plain(*parameters)
                                   for parameters in signatures_parameters))


@_bind_positionals.register(signatures.Overloaded)
def _(signature: signatures.Overloaded,
      args: Tuple[Domain, ...]) -> signatures.Base:
    sub_signatures = list(filter(methodcaller(signatures.Base.expects.__name__,
                                              *args),
                                 signature.signatures))
    if not sub_signatures:
        raise TypeError('No corresponding signature found.')
    return signatures.Overloaded(*map(functools.partial(_bind_positionals,
                                                        args=args),
                                      sub_signatures))


def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Given positional arguments will be added to the right end.
    """

    return Applier(function, *args, **kwargs)
