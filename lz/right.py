import functools
import itertools
from typing import (Callable,
                    Iterable,
                    List,
                    Sequence,
                    Tuple)

from paradigm.base import (OptionalParameter,
                           OverloadedSignature,
                           ParameterKind,
                           PlainSignature,
                           RequiredParameter)

from . import left
from ._core.right import Applier
from ._core.signatures import (Parameter,
                               Signature,
                               plain_signature_to_parameters_by_kind,
                               to_signature)
from .functional import (compose,
                         flip)
from .hints import (Domain,
                    Range)
from .iterating import expand
from .reversal import reverse


def accumulator(
        function: Callable[[Domain, Range], Range],
        initial: Range
) -> Callable[[Iterable[Domain]], Iterable[Iterable[Range]]]:
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


def attacher(_value: Domain) -> Callable[[Iterable[Domain]], Iterable[Domain]]:
    """
    Returns function that appends given object to iterable.

    >>> attach_hundred = attacher(100)
    >>> list(attach_hundred(range(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    """
    return Applier(attach, _value)


@functools.singledispatch
def attach(iterable: Iterable[Domain], _value: Domain) -> Iterable[Domain]:
    """
    Appends given object to the iterable.
    """
    yield from itertools.chain(iterable, expand(_value))


@attach.register(list)
def _(iterable: List[Domain], _value: Domain) -> List[Domain]:
    """
    Appends given object to the list.
    """
    return iterable + [_value]


@attach.register(tuple)
def _(iterable: Tuple[Domain, ...], object_: Domain) -> Tuple[Domain, ...]:
    """
    Appends given object to the tuple.
    """
    return iterable + (object_,)


def folder(function: Callable[[Domain, Range], Range],
           initial: Range) -> Callable[[Iterable[Domain]], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from right to left.

    >>> to_sum_evaluation_order = folder('({} + {})'.format, 0)
    >>> to_sum_evaluation_order(range(1, 10))
    '(1 + (2 + (3 + (4 + (5 + (6 + (7 + (8 + (9 + 0)))))))))'
    """
    left_folder = left.folder(flip(function), initial)
    return compose(left_folder, reverse)


@to_signature.register(Applier)
def _(value: Applier) -> Signature:
    return _bind_positionals_to_applier(
            to_signature(value.function).bind(**value.kwargs), value.args
    )


@functools.singledispatch
def _bind_positionals_to_applier(signature: Signature,
                                 args: Tuple[Domain, ...]) -> Signature:
    raise TypeError('Unsupported signature type: {type}.'
                    .format(type=type(signature)))


@_bind_positionals_to_applier.register(PlainSignature)
def _(signature: PlainSignature, args: Tuple[Domain, ...]) -> Signature:
    if not args:
        return signature
    parameters_by_kind = plain_signature_to_parameters_by_kind(signature)
    variadic_positionals = parameters_by_kind[
        ParameterKind.VARIADIC_POSITIONAL
    ]
    positionals = (parameters_by_kind[ParameterKind.POSITIONAL_ONLY]
                   + parameters_by_kind[ParameterKind.POSITIONAL_OR_KEYWORD])
    if len(args) > len(positionals) and not variadic_positionals:
        raise TypeError(f'Takes {len(positionals)} positional '
                        f'argument{"s" * (len(positionals) != 1)}, '
                        f'but {len(args)} '
                        f'{"was" if len(args) == 1 else "were"} given.')
    non_positionals = (parameters_by_kind[ParameterKind.KEYWORD_ONLY]
                       + parameters_by_kind[ParameterKind.VARIADIC_KEYWORD])
    signatures_parameters: List[Sequence[Parameter]] = []
    if len(args) <= len(positionals):
        signatures_parameters.append(positionals[:-len(args)]
                                     + non_positionals)
    if variadic_positionals:
        signatures_parameters.append(signature.parameters)
        for limit in range(1, len(args)):
            signatures_parameters.append(positionals[:-limit]
                                         + variadic_positionals
                                         + non_positionals)
    positionals_or_keywords = parameters_by_kind[
        ParameterKind.POSITIONAL_OR_KEYWORD
    ]
    optional_positionals_or_keywords = sum(
            map(OptionalParameter.__instancecheck__, positionals_or_keywords)
    )
    for offset in range(1, optional_positionals_or_keywords + 1):
        signatures_parameters.append(
                positionals[:-(len(args) + offset)]
                + [(OptionalParameter(annotation=parameter.annotation,
                                      **({'default': parameter.default}
                                         if parameter.has_default
                                         else {}),
                                      name=parameter.name,
                                      kind=ParameterKind.KEYWORD_ONLY)
                    if isinstance(parameter, OptionalParameter)
                    else RequiredParameter(annotation=parameter.annotation,
                                           kind=ParameterKind.KEYWORD_ONLY,
                                           name=parameter.name))
                   for parameter in positionals_or_keywords[-offset:]]
                + non_positionals
        )
    sub_signatures = [PlainSignature(*parameters,
                                     returns=signature.returns)
                      for parameters in signatures_parameters]
    return (sub_signatures[0]
            if len(sub_signatures) == 1
            else OverloadedSignature(*sub_signatures))


@_bind_positionals_to_applier.register(OverloadedSignature)
def _(signature: OverloadedSignature, args: Tuple[Domain, ...]) -> Signature:
    sub_signatures = [_bind_positionals_to_applier(sub_signature, args)
                      for sub_signature in signature.signatures
                      if sub_signature.expects(*args)]
    if not sub_signatures:
        raise TypeError('No corresponding signature found.')
    return (sub_signatures[0]
            if len(sub_signatures) == 1
            else OverloadedSignature(*sub_signatures))


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
