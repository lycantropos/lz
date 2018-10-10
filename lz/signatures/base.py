import inspect
import platform
from functools import (partial,
                       wraps)
from itertools import (repeat,
                       zip_longest)
from typing import (Callable,
                    Iterable,
                    Optional)

from lz.functional import (combine,
                           compose,
                           pack)
from lz.hints import (Map,
                      Range)
from lz.iterating import (expand,
                          flatten,
                          mapper,
                          reverse,
                          sifter)


class Parameter:
    kinds_prefixes = {inspect._VAR_POSITIONAL: '*',
                      inspect._VAR_KEYWORD: '**'}

    def __init__(self,
                 *,
                 name: str,
                 kind: inspect._ParameterKind,
                 has_default: bool) -> None:
        self.name = name
        self.kind = kind
        self.has_default = has_default

    def __repr__(self) -> str:
        return ''.join([self.kinds_prefixes.get(self.kind, ''),
                        self.name,
                        '=...' if self.has_default else ''])


class Signature:
    def __init__(self, *parameters: Parameter) -> None:
        self.parameters = parameters

    def __repr__(self) -> str:
        return '(' + ', '.join(map(repr, self.parameters)) + ')'


def factory(object_: Callable[..., Range]) -> Signature:
    raw_signature = inspect.signature(object_)

    def normalize_parameter(raw_parameter: inspect.Parameter) -> Parameter:
        has_default = raw_parameter.default is not inspect._empty
        return Parameter(name=raw_parameter.name,
                         kind=raw_parameter.kind,
                         has_default=has_default)

    parameters = map(normalize_parameter, raw_signature.parameters.values())
    return Signature(*parameters)


if platform.python_implementation() != 'PyPy':
    from typed_ast import ast3

    from . import arboretum


    def with_typeshed(function: Map[Callable[..., Range], Signature]
                      ) -> Map[Callable[..., Range], Signature]:
        @wraps(function)
        def wrapped(object_: Callable[..., Range]) -> Signature:
            try:
                return function(object_)
            except ValueError:
                from . import arboretum

                object_node = arboretum.to_node(object_)
                return from_ast(object_node.args)

        return wrapped


    factory = with_typeshed(factory)


    def from_ast(object_: ast3.arguments) -> Signature:
        parameters = to_parameters(object_)
        return Signature(*parameters)


    def to_positional_parameters(signature_ast: ast3.arguments
                                 ) -> Iterable[Parameter]:
        # double-reversing since parameters with default arguments go last
        parameters_with_defaults_ast = zip_longest(reverse(signature_ast.args),
                                                   signature_ast.defaults)
        parameters_with_defaults_ast = reverse(parameters_with_defaults_ast)
        parameter_factory = partial(to_parameter,
                                    kind=inspect._POSITIONAL_ONLY)
        parameters_factory = mapper(pack(parameter_factory))
        yield from parameters_factory(parameters_with_defaults_ast)


    def to_keyword_parameters(signature_ast: ast3.arguments
                              ) -> Iterable[Parameter]:
        parameters_with_defaults_ast = zip(signature_ast.kwonlyargs,
                                           signature_ast.kw_defaults)
        parameter_factory = partial(to_parameter,
                                    kind=inspect._KEYWORD_ONLY)
        parameters_factory = mapper(pack(parameter_factory))
        yield from parameters_factory(parameters_with_defaults_ast)


    def to_variadic_positional_parameter(signature_ast: ast3.arguments
                                         ) -> Optional[Parameter]:
        parameter_ast = signature_ast.vararg
        if parameter_ast is None:
            return None
        return Parameter(name=parameter_ast.arg,
                         kind=inspect._VAR_POSITIONAL,
                         has_default=False)


    def to_variadic_keyword_parameter(signature_ast: ast3.arguments
                                      ) -> Optional[Parameter]:
        parameter_ast = signature_ast.kwarg
        if parameter_ast is None:
            return None
        return Parameter(name=parameter_ast.arg,
                         kind=inspect._VAR_KEYWORD,
                         has_default=False)


    to_parameters = compose(
            sifter(),
            flatten,
            combine([to_positional_parameters,
                     compose(expand, to_variadic_positional_parameter),
                     to_keyword_parameters,
                     compose(expand, to_variadic_keyword_parameter)]),
            repeat)


    def to_parameter(parameter_ast: ast3.arg,
                     default_ast: Optional[ast3.expr],
                     *,
                     kind: inspect._ParameterKind) -> Parameter:
        return Parameter(name=parameter_ast.arg,
                         kind=kind,
                         has_default=default_ast is not None)
