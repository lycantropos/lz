import ast
import inspect
from functools import (lru_cache,
                       partial)
from itertools import (repeat,
                       zip_longest)
from operator import attrgetter
from typing import (Callable,
                    Dict,
                    Iterable,
                    List,
                    Optional)

from . import arboretum
from .functional import (combine,
                         compose,
                         pack)
from .hints import Range
from .iterating import (expand,
                        flatten,
                        grouper,
                        mapper,
                        reverse,
                        sifter)


class Parameter:
    def __init__(self,
                 *,
                 name: str,
                 kind: inspect._ParameterKind,
                 has_default: bool) -> None:
        self.name = name
        self.kind = kind
        self.has_default = has_default


class Signature:
    def __init__(self, *parameters: Parameter) -> None:
        self.parameters = parameters

    @property
    @lru_cache(None)
    def by_names(self) -> Dict[str, Parameter]:
        return {parameter.name: parameter
                for parameter in self.parameters}

    @property
    @lru_cache(None)
    def by_kinds(self) -> Dict[str, List[Parameter]]:
        return dict(grouper(attrgetter('kind'))(self.parameters))


def factory(object_: Callable[..., Range]) -> Signature:
    try:
        raw_signature = inspect.signature(object_)
    except ValueError:
        object_node = arboretum.to_node(object_)
        return from_ast(object_node.args)

    def normalize_parameter(raw_parameter: inspect.Parameter) -> Parameter:
        has_default = raw_parameter.default is not inspect._empty
        return Parameter(name=raw_parameter.name,
                         kind=raw_parameter.kind,
                         has_default=has_default)

    parameters = map(normalize_parameter, raw_signature.parameters.values())
    return Signature(*parameters)


def from_ast(object_: ast.arguments) -> Signature:
    to_parameters = compose(
            sifter(),
            flatten,
            combine(to_positional_parameters,
                    compose(expand, to_variadic_positional_parameter),
                    to_keyword_parameters,
                    compose(expand, to_variadic_keyword_parameter)),
            repeat)
    parameters = to_parameters(object_)
    return Signature(*parameters)


def to_positional_parameters(signature_ast: ast.arguments
                             ) -> Iterable[Parameter]:
    # double-reversing since parameters with default arguments go last
    parameters_with_defaults_ast = zip_longest(reverse(signature_ast.args),
                                               signature_ast.defaults)
    parameters_with_defaults_ast = reverse(parameters_with_defaults_ast)
    parameter_factory = partial(to_parameter,
                                kind=inspect._POSITIONAL_ONLY)
    yield from mapper(pack(parameter_factory))(parameters_with_defaults_ast)


def to_keyword_parameters(signature_ast: ast.arguments
                          ) -> Iterable[Parameter]:
    parameters_with_defaults_ast = zip(signature_ast.kwonlyargs,
                                       signature_ast.kw_defaults)
    parameter_factory = partial(to_parameter,
                                kind=inspect._KEYWORD_ONLY)
    yield from mapper(pack(parameter_factory))(parameters_with_defaults_ast)


def to_variadic_positional_parameter(signature_ast: ast.arguments
                                     ) -> Optional[Parameter]:
    parameter_ast = signature_ast.vararg
    if parameter_ast is None:
        return None
    return Parameter(name=parameter_ast.arg,
                     kind=inspect._VAR_POSITIONAL,
                     has_default=False)


def to_variadic_keyword_parameter(signature_ast: ast.arguments
                                  ) -> Optional[Parameter]:
    parameter_ast = signature_ast.kwarg
    if parameter_ast is None:
        return None
    return Parameter(name=parameter_ast.arg,
                     kind=inspect._VAR_KEYWORD,
                     has_default=False)


def to_parameter(parameter_ast: ast.arg,
                 default_ast: Optional[ast.expr],
                 *,
                 kind: inspect._ParameterKind) -> Parameter:
    return Parameter(name=parameter_ast.arg,
                     kind=kind,
                     has_default=default_ast is not None)
