import functools
import typing as _t

from paradigm.base import (OptionalParameter,
                           OverloadedSignature,
                           ParameterKind,
                           PlainSignature,
                           RequiredParameter)
from reprit import seekers
from reprit.base import generate_repr
from typing_extensions import final

from lz._core.functional import ApplierBase
from lz._core.signatures import (Parameter,
                                 Signature,
                                 plain_signature_to_parameters_by_kind,
                                 to_signature)

_Arg = _t.TypeVar('_Arg')
_KwArg = _t.TypeVar('_KwArg')
_Result = _t.TypeVar('_Result')
_T = _t.TypeVar('_T')


@final
class Applier(ApplierBase[_Arg, _KwArg, _Result]):
    def __init__(self,
                 function: _t.Callable[..., _Result],
                 *args: _Arg,
                 **kwargs: _KwArg) -> None:
        super().__init__(function, *args, **kwargs)

    def __call__(self, *args: _Arg, **kwargs: _KwArg) -> _Result:
        return self.function(*args, *self.args, **self.kwargs, **kwargs)

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)


@to_signature.register(Applier)
def _(value: Applier) -> Signature:
    return _bind_positionals_to_applier(
            to_signature(value.function).bind(**value.kwargs), value.args
    )


@functools.singledispatch
def _bind_positionals_to_applier(signature: Signature,
                                 args: _t.Tuple[_T, ...]) -> Signature:
    raise TypeError('Unsupported signature type: {type}.'
                    .format(type=type(signature)))


@_bind_positionals_to_applier.register(PlainSignature)
def _(signature: PlainSignature, args: _t.Tuple[_T, ...]) -> Signature:
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
    signatures_parameters: _t.List[_t.Sequence[Parameter]] = []
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
def _(signature: OverloadedSignature, args: _t.Tuple[_T, ...]) -> Signature:
    sub_signatures = [_bind_positionals_to_applier(sub_signature, args)
                      for sub_signature in signature.signatures
                      if sub_signature.expects(*args)]
    if not sub_signatures:
        raise TypeError('No corresponding signature found.')
    return (sub_signatures[0]
            if len(sub_signatures) == 1
            else OverloadedSignature(*sub_signatures))
