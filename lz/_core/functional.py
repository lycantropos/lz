import ast
import functools
import itertools
import sys
import typing as _t
from abc import (ABC,
                 abstractmethod)
from types import MethodType

from reprit import seekers
from reprit.base import generate_repr
from typing_extensions import (ParamSpec,
                               final)

from lz._core.signatures import (Signature,
                                 to_signature)

_Arg = _t.TypeVar('_Arg')
_KwArg = _t.TypeVar('_KwArg')
_Result = _t.TypeVar('_Result')
_T = _t.TypeVar('_T')

MIN_COMPOSABLE_FUNCTIONS_COUNT = 2


@final
class Composition(_t.Generic[_Arg, _KwArg, _Result]):
    _file_path: str
    _function: _t.Optional[_t.Callable[..., _t.Any]]
    _functions: _t.Tuple[_t.Callable[..., _t.Any], ...]
    _line_number: int
    _line_offset: int

    __slots__ = ('_file_path', '_function', '_functions', '_line_number',
                 '_line_offset')

    def __new__(cls,
                *functions: _t.Callable[..., _t.Any],
                file_path: _t.Optional[str] = None,
                line_number: int = 0,
                line_offset: int = 0) -> 'Composition':
        if len(functions) < MIN_COMPOSABLE_FUNCTIONS_COUNT:
            raise ValueError('Composition is defined '
                             f'for {MIN_COMPOSABLE_FUNCTIONS_COUNT} '
                             'or more functions, '
                             f'but got {len(functions)}.')
        self = super().__new__(cls)

        def flatten(
                function: _t.Callable[..., _t.Any]
        ) -> _t.Iterable[_t.Callable[..., _t.Any]]:
            if isinstance(function, cls):
                yield from function.functions
            else:
                yield function

        self._functions = tuple(itertools.chain.from_iterable(map(flatten,
                                                                  functions)))
        self._function = None
        if file_path is None:
            file_path = __file__
        self._file_path = file_path
        self._line_number = line_number
        self._line_offset = line_offset
        return self

    @property
    def functions(self) -> _t.Tuple[_t.Callable[..., _t.Any], ...]:
        return self._functions

    @property
    def function(self) -> _t.Callable[..., _Result]:
        if self._function is None:
            self._function = _compose(*self.functions,
                                      function_name='composition',
                                      file_path=self._file_path,
                                      line_number=self._line_number,
                                      line_offset=self._line_offset)
        return self._function

    def __call__(self, *args: _Arg, **kwargs: _KwArg) -> _Result:
        return self.function(*args, **kwargs)

    def __get__(self,
                instance: _T,
                owner: _t.Type[_T]) -> _t.Callable[..., _Result]:
        return MethodType(self.function, instance)

    def __getnewargs_ex__(self) -> _t.Tuple[_t.Tuple[_t.Any, ...],
                                            _t.Dict[str, _t.Any]]:
        return self.functions, {'file_path': self._file_path,
                                'line_number': self._line_number,
                                'line_offset': self._line_offset}

    __repr__ = generate_repr(__new__,
                             field_seeker=seekers.complex_)


@final
class Combination(_t.Generic[_Arg, _Result]):
    def __init__(self, *maps: _t.Callable[[_Arg], _Result]) -> None:
        self.maps = maps

    def __call__(self, arguments: _t.Iterable[_Arg]) -> _t.Tuple[_Result, ...]:
        return tuple(map_(argument)
                     for map_, argument in zip(self.maps, arguments))

    __repr__ = generate_repr(__init__)


class ApplierBase(ABC, _t.Generic[_Arg, _KwArg, _Result]):
    def __init__(self,
                 function: _t.Callable[..., _Result],
                 *args: _Arg,
                 **kwargs: _KwArg) -> None:
        if isinstance(function, type(self)):
            args = function.args + args
            kwargs = {**function.kwargs, **kwargs}
            function = function.function
        self._function = function
        self._args = args
        self._kwargs = kwargs

    @property
    def function(self) -> _t.Callable[..., _Result]:
        return self._function

    @property
    def args(self) -> _t.Tuple[_Arg, ...]:
        return self._args

    @property
    def kwargs(self) -> _t.Dict[str, _KwArg]:
        return self._kwargs

    @abstractmethod
    def __call__(self, *args: _Arg, **kwargs: _KwArg):
        pass


@final
class Curry(ApplierBase[_Arg, _KwArg, _Result]):
    def __init__(self,
                 function: _t.Callable[..., _Result],
                 _signature: Signature,
                 *args: _Arg,
                 **kwargs: _KwArg) -> None:
        super().__init__(function, *args, **kwargs)
        self._signature = _signature

    def __call__(self,
                 *args: _Arg,
                 **kwargs: _KwArg) -> _t.Union['Curry', _Result]:
        total_args = self.args + args
        total_kwargs = {**self.kwargs, **kwargs}
        try:
            return self.function(*total_args, **total_kwargs)
        except TypeError:
            if (not self._signature.expects(*total_args, **total_kwargs)
                    or self._signature.all_set(*total_args, **total_kwargs)):
                raise
            return type(self)(self.function, self._signature, *total_args,
                              **total_kwargs)

    def __getstate__(self) -> _t.Tuple[_t.Callable[..., _Result],
                                       _t.Tuple[_Arg, ...],
                                       _t.Dict[str, _KwArg]]:
        return self.function, self.args, self.kwargs

    def __setstate__(self,
                     state: _t.Tuple[_t.Callable[..., _Result],
                                     _t.Tuple[_Arg, ...],
                                     _t.Dict[str, _KwArg]]) -> None:
        self._function, self._args, self._kwargs = state
        self._signature = to_signature(self._function)

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)


@final
class Constant(_t.Generic[_T]):
    def __init__(self, _value: _T) -> None:
        self._value = _value

    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _T:
        return self._value

    __repr__ = generate_repr(__init__)


_Params = ParamSpec('_Params')


@final
class Cleavage(_t.Generic[_Result]):
    def __init__(self, *functions: _t.Callable[_Params, _Result]) -> None:
        self.functions = functions

    def __call__(self,
                 *args: _Params.args,
                 **kwargs: _Params.kwargs) -> _t.Tuple[_Result, ...]:
        return tuple(function(*args, **kwargs) for function in self.functions)


def _compose(*functions: _t.Callable[..., _t.Any],
             function_name: str,
             arguments_factory: _t.Callable[..., ast.arguments] =
             ast.arguments
             if sys.version_info < (3, 8)
             # Python3.8 adds positional-only arguments
             else _t.cast(_t.Callable[..., ast.arguments],
                          functools.partial(ast.arguments, [])),
             module_factory: _t.Callable[..., ast.Module] =
             ast.Module
             if sys.version_info < (3, 8)
             # Python3.8 adds `type_ignores` parameter
             else _t.cast(_t.Callable[..., ast.Module],
                          functools.partial(ast.Module,
                                            type_ignores=[])),
             file_path: str,
             line_number: int,
             line_offset: int) -> _t.Callable[..., _Result]:
    def function_to_unique_name(function: _t.Callable) -> str:
        # we are not using `__name__`/`__qualname__` attributes
        # due to their potential non-uniqueness
        return '_' + str(id(function)).replace('-', '_')

    functions_names = list(map(function_to_unique_name, functions))
    variadic_positionals_name = 'args'
    variadic_keywords_name = 'kwargs'

    def to_next_call_node(node: ast.Call, name: str) -> ast.Call:
        return ast.Call(to_name_node(name), [node], [],
                        lineno=line_number,
                        col_offset=line_offset)

    def to_name_node(name: str,
                     *,
                     context_factory: _t.Type[ast.expr_context] = ast.Load
                     ) -> ast.Name:
        return ast.Name(name, context_factory(),
                        lineno=line_number,
                        col_offset=line_offset)

    reversed_functions_names = reversed(functions_names)
    calls_node = ast.Call(
            to_name_node(next(reversed_functions_names)),
            [ast.Starred(to_name_node(variadic_positionals_name),
                         ast.Load(),
                         lineno=line_number,
                         col_offset=line_offset)],
            [ast.keyword(None, to_name_node(variadic_keywords_name),
                         lineno=line_number,
                         col_offset=line_offset)],
            lineno=line_number,
            col_offset=line_offset
    )
    calls_node = functools.reduce(to_next_call_node,
                                  reversed_functions_names,
                                  calls_node)
    function_definition_node = ast.FunctionDef(
            function_name,
            arguments_factory(
                    [],
                    ast.arg(variadic_positionals_name, None,
                            lineno=line_number,
                            col_offset=line_offset),
                    [],
                    [],
                    ast.arg(variadic_keywords_name, None,
                            lineno=line_number,
                            col_offset=line_offset),
                    []),
            [ast.Return(calls_node,
                        lineno=line_number,
                        col_offset=line_offset)],
            [],
            None,
            lineno=line_number,
            col_offset=line_offset
    )
    tree = module_factory([function_definition_node])
    code = compile(tree, file_path, 'exec')
    namespace = dict(zip(functions_names, functions))
    exec(code, namespace)
    return namespace[function_name]


@to_signature.register(Cleavage)
def _(_value: Cleavage) -> Signature:
    return to_signature(_value.functions[0])


@to_signature.register(Combination)
def _(_value: Combination) -> Signature:
    return to_signature(_value.__call__)


@to_signature.register(Composition)
def _(_value: Composition) -> Signature:
    return to_signature(_value.functions[-1])


@to_signature.register(Constant)
def _(_value: Constant) -> Signature:
    return to_signature(_value.__call__)


@to_signature.register(Curry)
def _(_value: Curry) -> Signature:
    return _value._signature
