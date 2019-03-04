import ast
import functools
import inspect
import itertools
import textwrap
from collections import abc
from contextlib import suppress
from operator import add
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Dict,
                    Iterable,
                    Optional,
                    Tuple,
                    Type,
                    Union)

from paradigm import signatures

from .hints import (Domain,
                    Map,
                    Operator,
                    Range)


def identity(argument: Domain) -> Domain:
    """
    Returns object itself.
    """
    return argument


def to_composition_name(*functions: Callable) -> str:
    @functools.singledispatch
    def function_to_name(function: Callable) -> str:
        return function.__name__

    @function_to_name.register(ApplierBase)
    def applier_to_name(function: ApplierBase) -> str:
        return function_to_name(function.func)

    return 'composition_of_' + '_and_'.join(map(function_to_name, functions))


def to_composition_docstring(*functions: Callable,
                             tab_size: int = 4,
                             name_wrapper: Operator[str] = '"{}"'.format
                             ) -> str:
    def function_to_sub_docstring(function: Callable) -> str:
        view_name = function_to_view_name(function)
        try:
            docstring = function.__doc__
        except AttributeError:
            return name_wrapper(view_name)
        else:
            if docstring is None:
                return name_wrapper(view_name)
            return (name_wrapper(view_name) + ':\n'
                    + textwrap.indent(docstring,
                                      prefix=' ' * tab_size))

    @functools.singledispatch
    def function_to_view_name(function: Callable) -> str:
        return function.__qualname__

    @function_to_view_name.register(ApplierBase)
    def applier_to_view_name(function: ApplierBase) -> str:
        return function_to_view_name(function.func)

    sub_docstrings = itertools.starmap('{}. {}'.format,
                                       enumerate(map(function_to_sub_docstring,
                                                     functions),
                                                 start=1))
    return ('Composition of next {count} functions:\n'
            '{sub_docstrings}'
            .format(count=len(functions),
                    sub_docstrings='\n'.join(sub_docstrings)))


def compose(last_function: Map[Any, Range],
            *front_functions: Callable[..., Any],
            name_factory: Callable[..., str] = to_composition_name,
            docstring_factory: Callable[..., str] = to_composition_docstring
            ) -> Callable[..., Range]:
    """
    Returns functions composition.
    """
    if not front_functions:
        return last_function

    functions = (last_function,) + front_functions

    def function_to_unique_name(function: Callable) -> str:
        # we are not using ``__name__``/``__qualname__`` attributes
        # due to their potential non-uniqueness
        return '_' + str(hash(function)).replace('-', '_')

    functions_names = list(map(function_to_unique_name, functions))

    caller_frame_info = inspect.stack()[1]
    col_offset = 0
    lineno = caller_frame_info.lineno
    set_attributes = functools.partial(functools.partial,
                                       lineno=lineno,
                                       col_offset=col_offset)

    variadic_positionals_name = 'args'
    variadic_keywords_name = 'kwargs'

    def to_next_call_node(node: ast.Call, name: str) -> ast.Call:
        return set_attributes(ast.Call)(to_name_node(name), [node], [])

    def to_name_node(name: str,
                     *,
                     context_factory: Type[ast.expr_context] = ast.Load
                     ) -> ast.Name:
        return set_attributes(ast.Name)(name, context_factory())

    reversed_functions_names = reversed(functions_names)
    calls_node = set_attributes(ast.Call)(
            to_name_node(next(reversed_functions_names)),
            [set_attributes(ast.Starred)(
                    to_name_node(variadic_positionals_name),
                    ast.Load())],
            [ast.keyword(None,
                         to_name_node(variadic_keywords_name))])
    calls_node = functools.reduce(to_next_call_node,
                                  reversed_functions_names,
                                  calls_node)
    function_name = to_composition_name(*functions)
    function_definition_node = set_attributes(ast.FunctionDef)(
            function_name,
            ast.arguments([],
                          set_attributes(ast.arg)(variadic_positionals_name,
                                                  None),
                          [],
                          [],
                          set_attributes(ast.arg)(variadic_keywords_name,
                                                  None),
                          []),
            [set_attributes(ast.Return)(calls_node)],
            [],
            None)
    tree = ast.Module([function_definition_node])
    code = compile(tree, caller_frame_info.filename, 'exec')
    namespace = dict(zip(functions_names, functions))
    exec(code, namespace)
    result = namespace[function_name]
    result.__doc__ = docstring_factory(*functions)
    return result


def combine(*maps: Map) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies each map to corresponding argument.
    """

    def combined(arguments: Iterable[Domain]) -> Iterable[Range]:
        yield from (map_(argument)
                    for map_, argument in zip(maps, arguments))

    return combined


class ApplierBase(abc.Callable):
    def __init__(self, function: Callable[..., Range],
                 *args: Domain,
                 **kwargs: Domain) -> None:
        if isinstance(function, type(self)):
            args = function.args + args
            kwargs = {**function.keywords, **kwargs}
            function = function.func
        self.func = function
        self.args = args
        self.keywords = kwargs

    def __repr__(self) -> str:
        arguments_strings = itertools.chain(
                [repr(self.func)],
                arguments_to_strings(self.args, self.keywords))
        cls = type(self)
        return (cls.__module__ + '.' + cls.__qualname__
                + '(' + ', '.join(arguments_strings) + ')')


ApplierBase.register(functools.partial)


class Curry(ApplierBase):
    def __init__(self,
                 function: Callable[..., Range],
                 signature: signatures.Base,
                 *args: Domain,
                 **kwargs: Domain) -> None:
        super().__init__(function, *args, **kwargs)
        self.signature = signature

    def __call__(self, *args: Domain, **kwargs: Domain
                 ) -> Union['Curry', Range]:
        args = self.args + args
        kwargs = {**self.keywords, **kwargs}
        try:
            return self.func(*args, **kwargs)
        except TypeError:
            if not self.signature.has_unset_parameters(*args, **kwargs):
                raise
        return type(self)(self.func, self.signature, *args, **kwargs)


def arguments_to_strings(positional_arguments: Tuple[Any, ...],
                         keyword_arguments: Dict[str, Any]) -> Iterable[str]:
    yield from map(repr, positional_arguments)
    yield from itertools.starmap('{}={!r}'.format, keyword_arguments.items())


def curry(function: Callable[..., Range],
          *,
          signature: Optional[signatures.Base] = None) -> Curry:
    """
    Returns curried version of given function.
    """
    if signature is None:
        signature = signatures.factory(function)
    return Curry(function, signature)


def pack(function: Callable[..., Range]) -> Map[Iterable[Domain], Range]:
    """
    Returns function that works with single iterable parameter
    by unpacking elements to given function.
    """

    def packed(args: Iterable[Domain],
               kwargs: Dict[str, Any] = MappingProxyType({})) -> Range:
        return function(*args, **kwargs)

    members_factories = dict(members_copiers)
    members_factories['__name__'] = functools.partial(add, 'packed ')
    members_factories['__qualname__'] = functools.partial(add, 'packed ')
    update_metadata(function, packed,
                    members_factories=members_factories)
    return packed


def to_constant(object_: Domain) -> Callable[..., Domain]:
    """
    Returns function that returns given object.
    """

    def constant(*_: Domain, **__: Domain) -> Domain:
        return object_

    object_repr = repr(object_)
    constant.__name__ = object_repr + ' constant'
    constant.__qualname__ = object_repr + ' constant'
    constant.__doc__ = 'Returns {}.'.format(object_repr)
    return constant


def flip(function: Callable[..., Range]) -> Callable[..., Range]:
    """
    Returns function with positional arguments flipped.
    """

    def flipped(*args, **kwargs) -> Range:
        return function(*args[::-1], **kwargs)

    members_factories = dict(members_copiers)
    members_factories['__name__'] = functools.partial(add, 'flipped ')
    members_factories['__qualname__'] = functools.partial(add, 'flipped ')
    update_metadata(function, flipped,
                    members_factories=members_factories)
    return flipped


def cleave(*functions: Callable[..., Range]) -> Callable[..., Iterable[Range]]:
    """
    Returns function that separately applies
    given functions to the same arguments.
    """

    def cleft(*args, **kwargs) -> Range:
        yield from (function(*args, **kwargs)
                    for function in functions)

    return cleft


members_copiers = dict(itertools.chain(zip(functools.WRAPPER_ASSIGNMENTS,
                                           itertools.repeat(identity))))


def update_metadata(source_function: Callable[..., Range],
                    target_function: Callable[..., Range],
                    *,
                    members_factories: Dict[str, Operator]) -> None:
    for member_name, member_factory in members_factories.items():
        try:
            source_member = getattr(source_function, member_name)
        except AttributeError:
            continue
        else:
            target_member = member_factory(source_member)
            setattr(target_function, member_name, target_member)
    with suppress(AttributeError):
        target_function.__dict__.update(source_function.__dict__)
