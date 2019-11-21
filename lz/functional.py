import ast
import functools
import inspect
import itertools
import sys
from collections import abc
from types import (MappingProxyType,
                   MethodType)
from typing import (Any,
                    Callable,
                    Dict,
                    Iterable,
                    Optional,
                    Tuple,
                    Type,
                    Union)

from paradigm import signatures
from reprit import seekers
from reprit.base import generate_repr

from .hints import (Domain,
                    Map,
                    Range)


def identity(argument: Domain) -> Domain:
    """
    Returns object itself.

    >>> identity(0)
    0
    """
    return argument


def compose(last_function: Map[Any, Range],
            *front_functions: Callable[..., Any]) -> Callable[..., Range]:
    """
    Returns functions composition.

    >>> sum_of_first_n_natural_numbers = compose(sum, range)
    >>> sum_of_first_n_natural_numbers(10)
    45
    """
    caller_frame_info = inspect.stack()[1]
    return Composition(last_function, *front_functions,
                       file_path=caller_frame_info.filename,
                       line_number=caller_frame_info.lineno,
                       line_offset=0)


class Composition:
    def __new__(cls,
                *functions: Callable[..., Any],
                **kwargs: Any) -> Union['Composition', Callable[..., Range]]:
        if len(functions) == 1:
            return functions[0]
        return super().__new__(cls)

    def __init__(self,
                 *functions: Callable[..., Any],
                 file_path: Optional[str] = None,
                 line_number: int = 0,
                 line_offset: int = 0) -> None:
        def flatten(function: Callable[..., Any]
                    ) -> Iterable[Callable[..., Any]]:
            if isinstance(function, type(self)):
                yield from function.functions
            else:
                yield function

        self._functions = tuple(itertools.chain
                                .from_iterable(map(flatten, functions)))
        self._function = None
        if file_path is None:
            file_path = __file__
        self._file_path = file_path
        self._line_number = line_number
        self._line_offset = line_offset

    @property
    def functions(self) -> Tuple[Callable[..., Any], ...]:
        return self._functions

    @property
    def function(self) -> Callable[..., Range]:
        if self._function is None:
            self._function = _compose(*self.functions,
                                      function_name='composition',
                                      file_path=self._file_path,
                                      line_number=self._line_number,
                                      line_offset=self._line_offset)
        return self._function

    def __call__(self, *args: Domain, **kwargs: Domain) -> Range:
        return self.function(*args, **kwargs)

    def __get__(self,
                instance: Domain,
                owner: Type[Domain]) -> Callable[..., Range]:
        return MethodType(self.function, instance)

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)


@signatures.factory.register(Composition)
def _(object_: Composition) -> signatures.Base:
    return signatures.factory(object_.functions[-1])


def _compose(*functions: Callable[..., Any],
             function_name: str,
             arguments_factory: Callable[..., ast.arguments] =
             ast.arguments if sys.version_info < (3, 8)
             # Python3.8 adds positional-only arguments
             else functools.partial(ast.arguments, []),
             module_factory: Callable[..., ast.Module] =
             ast.Module if sys.version_info < (3, 8)
             # Python3.8 adds `type_ignores` parameter
             else functools.partial(ast.Module,
                                    type_ignores=[]),
             file_path: str,
             line_number: int,
             line_offset: int) -> Callable[..., Range]:
    def function_to_unique_name(function: Callable) -> str:
        # we are not using `__name__`/`__qualname__` attributes
        # due to their potential non-uniqueness
        return '_' + str(id(function)).replace('-', '_')

    functions_names = list(map(function_to_unique_name, functions))

    set_attributes = functools.partial(functools.partial,
                                       lineno=line_number,
                                       col_offset=line_offset)

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
    function_definition_node = set_attributes(ast.FunctionDef)(
            function_name,
            arguments_factory(
                    [],
                    set_attributes(ast.arg)(variadic_positionals_name, None),
                    [],
                    [],
                    set_attributes(ast.arg)(variadic_keywords_name, None),
                    []),
            [set_attributes(ast.Return)(calls_node)],
            [],
            None)
    tree = module_factory([function_definition_node])
    code = compile(tree, file_path, 'exec')
    namespace = dict(zip(functions_names, functions))
    exec(code, namespace)
    return namespace[function_name]


def combine(*maps: Map) -> Map[Iterable[Domain], Iterable[Range]]:
    """
    Returns function that applies each map to corresponding argument.

    >>> encoder_decoder = combine(str.encode, bytes.decode)
    >>> list(encoder_decoder(['hello', b'world']))
    [b'hello', 'world']
    """
    return Combination(*maps)


class Combination:
    def __init__(self, *maps: Map) -> None:
        self.maps = maps

    def __call__(self, arguments: Iterable[Domain]) -> Iterable[Range]:
        yield from (map_(argument)
                    for map_, argument in zip(self.maps, arguments))

    __repr__ = generate_repr(__init__)


@signatures.factory.register(Combination)
def _(object_: Combination) -> signatures.Base:
    return signatures.factory(object_.__call__)


class ApplierBase(abc.Callable):
    def __init__(self, function: Callable[..., Range],
                 *args: Domain,
                 **kwargs: Domain) -> None:
        if isinstance(function, type(self)):
            args = function.args + args
            kwargs = {**function.keywords, **kwargs}
            function = function.func
        self._function = function
        self._args = args
        self._kwargs = kwargs

    @property
    def func(self) -> Callable[..., Range]:
        return self._function

    @property
    def args(self) -> Tuple[Domain, ...]:
        return self._args

    @property
    def keywords(self) -> Dict[str, Domain]:
        return self._kwargs


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
            if (not self.signature.expects(*args, **kwargs)
                    or self.signature.all_set(*args, **kwargs)):
                raise
        return type(self)(self.func, self.signature, *args, **kwargs)

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)


@signatures.factory.register(Curry)
def _(object_: Curry) -> signatures.Base:
    return object_.signature


def curry(function: Callable[..., Range],
          *,
          signature: Optional[signatures.Base] = None) -> Curry:
    """
    Returns curried version of given function.

    >>> curried_pow = curry(pow)
    >>> two_to_power = curried_pow(2)
    >>> two_to_power(10)
    1024
    """
    if signature is None:
        signature = signatures.factory(function)
    return Curry(function, signature)


def pack(function: Callable[..., Range]) -> Map[Iterable[Domain], Range]:
    """
    Returns function that works with single iterable parameter
    by unpacking elements to given function.

    >>> packed_int = pack(int)
    >>> packed_int(['10'])
    10
    >>> packed_int(['10'], {'base': 2})
    2
    """
    return functools.partial(apply, function)


def apply(function: Callable[..., Range],
          args: Iterable[Domain],
          kwargs: Dict[str, Any] = MappingProxyType({})) -> Range:
    """
    Calls given function with given positional and keyword arguments.
    """
    return function(*args, **kwargs)


def to_constant(object_: Domain) -> Callable[..., Domain]:
    """
    Returns function that always returns given object.

    >>> always_zero = to_constant(0)
    >>> always_zero()
    0
    >>> always_zero(1)
    0
    >>> always_zero(how_about=2)
    0
    """
    return Constant(object_)


class Constant:
    def __init__(self, object_: Domain) -> None:
        self.object_ = object_

    def __call__(self, *args: Any, **kwargs: Any) -> Domain:
        return self.object_

    __repr__ = generate_repr(__init__)


@signatures.factory.register(Constant)
def _(object_: Constant) -> signatures.Base:
    return signatures.factory(object_.__call__)


def flip(function: Callable[..., Range]) -> Callable[..., Range]:
    """
    Returns function with positional arguments flipped.

    >>> flipped_power = flip(pow)
    >>> flipped_power(2, 4)
    16
    """
    return functools.partial(call_flipped, function)


def call_flipped(function: Callable[..., Range],
                 *args: Domain,
                 **kwargs: Domain) -> Range:
    """
    Calls given function with positional arguments flipped.
    """
    return function(*args[::-1], **kwargs)


def cleave(*functions: Callable[..., Range]) -> Callable[..., Iterable[Range]]:
    """
    Returns function that separately applies
    given functions to the same arguments.

    >>> to_min_and_max = cleave(min, max)
    >>> list(to_min_and_max(range(10)))
    [0, 9]
    >>> list(to_min_and_max(range(0), default=None))
    [None, None]
    """
    return Cleavage(*functions)


class Cleavage:
    def __init__(self, *functions: Map) -> None:
        self.functions = functions

    def __call__(self, *args: Domain, **kwargs: Domain) -> Iterable[Range]:
        yield from (function(*args, **kwargs)
                    for function in self.functions)

    __repr__ = generate_repr(__init__)


@signatures.factory.register(Cleavage)
def _(object_: Cleavage) -> signatures.Base:
    return signatures.factory(object_.__call__)


def flatmap(function: Map[Domain, Iterable[Range]],
            *iterables: Iterable[Domain]) -> Iterable[Range]:
    """
    Applies given function to the arguments aggregated from given iterables
    and concatenates results into plain iterable.

    >>> list(flatmap(range, range(5)))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3]
    """
    yield from itertools.chain.from_iterable(map(function, *iterables))
