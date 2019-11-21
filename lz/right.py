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

    >>> def to_next_fraction(partial_denominator: int,
    ...                      reciprocal: float) -> float:
    ...     return partial_denominator + 1 / reciprocal
    >>> to_simple_continued_fractions = accumulator(to_next_fraction, 1)
    >>> from itertools import repeat
    >>> [round(fraction, 4)
    ...  for fraction in to_simple_continued_fractions(list(repeat(1, 10)))]
    [1, 2.0, 1.5, 1.6667, 1.6, 1.625, 1.6154, 1.619, 1.6176, 1.6182, 1.618]
    """
    left_accumulator = left.accumulator(flip(function), initial)
    return compose(left_accumulator, reverse)


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    """
    Returns function that appends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    """
    return functools.partial(attach,
                             object_=object_)


@functools.singledispatch
def attach(iterable: Iterable[Domain],
           object_: Domain) -> Iterable[Domain]:
    """
    Appends given object to the iterable.
    """
    yield from itertools.chain(iterable, expand(object_))


@attach.register(list)
def _(iterable: List[Domain],
      object_: Domain) -> List[Domain]:
    """
    Appends given object to the list.
    """
    return iterable + [object_]


@attach.register(tuple)
def _(iterable: Tuple[Domain, ...],
      object_: Domain) -> Tuple[Domain, ...]:
    """
    Appends given object to the tuple.
    """
    return iterable + (object_,)


def folder(function: Callable[[Domain, Range], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from right to left.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(range(1, 10))
    '(1 + (2 + (3 + (4 + (5 + (6 + (7 + (8 + (9 + 0)))))))))'
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

    >>> square = applier(pow, 2)
    >>> square(10)
    100
    """
    return Applier(function, *args, **kwargs)
