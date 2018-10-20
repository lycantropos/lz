import enum
import inspect
import platform
from abc import (ABC,
                 abstractmethod)
from collections import defaultdict
from functools import (partial,
                       singledispatch,
                       wraps)
from itertools import (repeat,
                       zip_longest)
from operator import attrgetter
from types import (BuiltinFunctionType,
                   BuiltinMethodType,
                   FunctionType,
                   MethodType)
from typing import (Callable,
                    Iterable,
                    Optional)

from lz import right
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
from .hints import (MethodDescriptorType,
                    WrapperDescriptorType)


class Parameter:
    class Kind(enum.IntEnum):
        POSITIONAL_ONLY = 0
        POSITIONAL_OR_KEYWORD = 1
        VARIADIC_POSITIONAL = 2
        KEYWORD_ONLY = 3
        VARIADIC_KEYWORD = 4

        def __repr__(self) -> str:
            return type(self).__qualname__ + '.' + self._name_

    kinds_prefixes = defaultdict(str,
                                 {Kind.VARIADIC_POSITIONAL: '*',
                                  Kind.VARIADIC_KEYWORD: '**'})

    def __init__(self,
                 *,
                 name: str,
                 kind: Kind,
                 has_default: bool) -> None:
        self.name = name
        self.kind = kind
        self.has_default = has_default

    def __eq__(self, other: 'Parameter') -> bool:
        if not isinstance(other, Parameter):
            return NotImplemented
        return (self.name == other.name
                and self.kind == other.kind
                and self.has_default is other.has_default)

    def __hash__(self) -> int:
        return hash((self.name, self.kind, self.has_default))

    def __repr__(self) -> str:
        return ''.join([self.kinds_prefixes[self.kind],
                        self.name,
                        '=...' if self.has_default else ''])


class Base(ABC):
    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: 'Base') -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass


class Plain(Base):
    def __init__(self, *parameters: Parameter) -> None:
        self.parameters = parameters

    def __eq__(self, other: Base) -> bool:
        if not isinstance(other, Base):
            return NotImplemented
        if not isinstance(other, Plain):
            return False
        return self.parameters == other.parameters

    def __hash__(self) -> int:
        return hash(self.parameters)

    def __repr__(self) -> str:
        return '(' + ', '.join(map(repr, self.parameters)) + ')'


@singledispatch
def factory(object_: Callable[..., Range]) -> Base:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


def from_callable(object_: Callable[..., Range]) -> Base:
    raw_signature = inspect.signature(object_)

    def normalize_parameter(raw_parameter: inspect.Parameter) -> Parameter:
        has_default = raw_parameter.default is not inspect._empty
        return Parameter(name=raw_parameter.name,
                         kind=Parameter.Kind(raw_parameter.kind),
                         has_default=has_default)

    parameters = map(normalize_parameter, raw_signature.parameters.values())
    return Plain(*parameters)


@singledispatch
def slice_parameters(signature: Base,
                     slice_: slice) -> Base:
    raise TypeError('Unsupported signature type: {type}.'
                    .format(type=type(signature)))


@slice_parameters.register(Plain)
def slice_plain_parameters(signature: Plain,
                           slice_: slice) -> Base:
    return Plain(*signature.parameters[slice_])


if platform.python_implementation() == 'PyPy':
    from lz.iterating import slider


    @factory.register(type)
    def from_class(object_: type) -> Base:
        try:
            return from_callable(object_)
        except ValueError:
            method = None
            for cls, next_cls in slider(2)(object_.__mro__):
                if cls.__new__ is not next_cls.__new__:
                    method = cls.__new__
                    break
                elif cls.__init__ is not next_cls.__init__:
                    method = cls.__init__
                    break
            if method is None:
                raise
            return slice_parameters(factory(method), slice(1, None))
else:
    from typed_ast import ast3

    from . import arboretum
    from . import catalog


    class Overloaded(Base):
        def __init__(self, *signatures: Base) -> None:
            self.signatures = frozenset(signatures)

        def __eq__(self, other: Base) -> bool:
            if not isinstance(other, Base):
                return NotImplemented
            if not isinstance(other, Overloaded):
                return False
            return self.signatures == other.signatures

        def __hash__(self) -> int:
            return hash(self.signatures)

        def __repr__(self) -> str:
            return '\nor\n'.join(map(repr, self.signatures))


    def with_typeshed(function: Map[Callable[..., Range], Base]
                      ) -> Map[Callable[..., Range], Base]:
        @wraps(function)
        def wrapped(object_: Callable[..., Range]) -> Base:
            try:
                return function(object_)
            except ValueError as error:
                object_path = catalog.factory(object_)
                module_path = catalog.factory(catalog
                                              .module_name_factory(object_))
                try:
                    object_nodes = arboretum.to_nodes(object_path, module_path)
                except KeyError:
                    raise error
                try:
                    return flatten_signatures(to_signatures(object_nodes))
                except AttributeError:
                    raise error

        return wrapped


    from_callable = with_typeshed(from_callable)


    @factory.register(type)
    def from_class(object_: type) -> Base:
        try:
            return from_callable(object_)
        except ValueError:
            method_path = (catalog.factory(object_)
                           .join(catalog.factory('__init__')))
            module_path = catalog.factory(catalog
                                          .module_name_factory(object_))
            method_nodes = arboretum.to_nodes(method_path, module_path)
            method_signature = flatten_signatures(to_signatures(method_nodes))
            return slice_parameters(method_signature, slice(1, None))


    def flatten_signatures(signatures: Iterable[Base]) -> Base:
        signatures = list(signatures)
        try:
            signature, = signatures
        except ValueError:
            return Overloaded(*signatures)
        else:
            return signature


    @slice_parameters.register(Overloaded)
    def slice_overloaded_parameters(signature: Overloaded,
                                    slice_: slice) -> Base:
        return Overloaded(*map(partial(slice_parameters,
                                       slice_=slice_),
                               signature.signatures))


    def from_ast(object_: ast3.arguments) -> Base:
        parameters = to_parameters(object_)
        return Plain(*parameters)


    to_signatures = mapper(compose(from_ast, attrgetter('args')))


    def to_positional_parameters(signature_ast: ast3.arguments
                                 ) -> Iterable[Parameter]:
        # double-reversing since parameters with default arguments go last
        parameters_with_defaults_ast = zip_longest(reverse(signature_ast.args),
                                                   signature_ast.defaults)
        parameters_with_defaults_ast = reverse(parameters_with_defaults_ast)
        parameter_factory = partial(to_parameter,
                                    kind=Parameter.Kind.POSITIONAL_ONLY)
        parameters_factory = mapper(pack(parameter_factory))
        yield from parameters_factory(parameters_with_defaults_ast)


    def to_keyword_parameters(signature_ast: ast3.arguments
                              ) -> Iterable[Parameter]:
        parameters_with_defaults_ast = zip(signature_ast.kwonlyargs,
                                           signature_ast.kw_defaults)
        parameter_factory = partial(to_parameter,
                                    kind=Parameter.Kind.KEYWORD_ONLY)
        parameters_factory = mapper(pack(parameter_factory))
        yield from parameters_factory(parameters_with_defaults_ast)


    def to_variadic_positional_parameter(signature_ast: ast3.arguments
                                         ) -> Optional[Parameter]:
        parameter_ast = signature_ast.vararg
        if parameter_ast is None:
            return None
        return Parameter(name=parameter_ast.arg,
                         kind=Parameter.Kind.VARIADIC_POSITIONAL,
                         has_default=False)


    def to_variadic_keyword_parameter(signature_ast: ast3.arguments
                                      ) -> Optional[Parameter]:
        parameter_ast = signature_ast.kwarg
        if parameter_ast is None:
            return None
        return Parameter(name=parameter_ast.arg,
                         kind=Parameter.Kind.VARIADIC_KEYWORD,
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
                     kind: Parameter.Kind) -> Parameter:
        return Parameter(name=parameter_ast.arg,
                         kind=kind,
                         has_default=default_ast is not None)

from_callable = right.folder(factory.register, from_callable)([
    BuiltinFunctionType,
    BuiltinMethodType,
    FunctionType,
    MethodType,
    MethodDescriptorType,
    WrapperDescriptorType])
