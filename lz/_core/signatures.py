import functools
from typing import (Any,
                    Dict,
                    List,
                    Union)

from paradigm.base import (OptionalParameter,
                           OverloadedSignature,
                           ParameterKind,
                           PlainSignature,
                           RequiredParameter,
                           signature_from_callable)

Signature = Union[PlainSignature, OverloadedSignature]
Parameter = Union[OptionalParameter, RequiredParameter]


@functools.singledispatch
def to_signature(value: Any) -> Signature:
    return signature_from_callable(value)


def plain_signature_to_parameters_by_kind(
        signature: PlainSignature
) -> Dict[ParameterKind, List[Parameter]]:
    result: Dict[ParameterKind, List[Parameter]] = {kind: []
                                                    for kind in ParameterKind}
    for parameter in signature.parameters:
        result[parameter.kind].append(parameter)
    return result
