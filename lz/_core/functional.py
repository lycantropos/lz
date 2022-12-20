import ast
import functools
import itertools
import sys
import typing as _t
from abc import (ABC,
                 abstractmethod)
from types import MethodType

from paradigm.base import (OverloadedSignature,
                           PlainSignature)
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
    _function: _t.Callable[..., _t.Any]
    _functions: _t.Tuple[_t.Callable[..., _t.Any], ...]
    _line_number: int
    _line_offset: int

    __slots__ = ('_file_path', '_function', '_functions', '_line_number',
                 '_line_offset')

    def __new__(cls,
                *functions: _t.Callable[..., _t.Any],
                file_path: str = __file__,
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
                yield from function._functions
            else:
                yield function

        self._functions = tuple(itertools.chain.from_iterable(map(flatten,
                                                                  functions)))
        self._file_path = file_path
        self._line_number = line_number
        self._line_offset = line_offset
        self._function = _compose(*functions,
                                  function_name='composition',
                                  file_path=file_path,
                                  line_number=line_number,
                                  line_offset=line_offset)
        return self

    def __call__(self, *args: _Arg, **kwargs: _KwArg) -> _Result:
        return self._function(*args, **kwargs)

    def __get__(self,
                instance: _T,
                owner: _t.Type[_T]) -> _t.Callable[..., _Result]:
        return MethodType(self, instance)

    def __getnewargs_ex__(self) -> _t.Tuple[_t.Tuple[_t.Any, ...],
                                            _t.Dict[str, _t.Any]]:
        return self._functions, {'file_path': self._file_path,
                                 'line_number': self._line_number,
                                 'line_offset': self._line_offset}

    def __getstate__(self) -> None:
        return None

    def __setstate__(self, _state: None) -> None:
        pass

    __repr__ = generate_repr(__new__,
                             field_seeker=seekers.complex_)


@final
class Combination(_t.Generic[_Arg, _Result]):
    _file_path: str
    _function: _t.Callable[..., _t.Tuple[_Result, ...]]
    _line_number: int
    _line_offset: int
    _maps: _t.Tuple[_t.Callable[[_Arg], _Result], ...]

    __slots__ = ('_file_path', '_function', '_line_number', '_line_offset',
                 '_maps')

    def __new__(cls,
                *_maps: _t.Callable[[_Arg], _Result],
                file_path: str = __file__,
                line_number: int = 0,
                line_offset: int = 0) -> 'Combination[_Arg, _Result]':
        self = super().__new__(cls)
        self._maps = _maps
        self._file_path = file_path
        self._line_number = line_number
        self._line_offset = line_offset
        self._function = _combine(*_maps,
                                  function_name='combination',
                                  file_path=file_path,
                                  line_number=line_number,
                                  line_offset=line_offset)
        return self

    def __call__(self, *args: _Arg) -> _t.Tuple[_Result, ...]:
        return self._function(*args)

    def __getnewargs_ex__(self) -> _t.Tuple[_t.Tuple[_t.Any, ...],
                                            _t.Dict[str, _t.Any]]:
        return self._maps, {'file_path': self._file_path,
                            'line_number': self._line_number,
                            'line_offset': self._line_offset}

    def __getstate__(self) -> None:
        return None

    def __setstate__(self, _state: None) -> None:
        pass

    __repr__ = generate_repr(__new__,
                             field_seeker=seekers.complex_)


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

if sys.version_info < (3, 10):
    @final
    class Cleavage(_t.Generic[_Result]):
        _file_path: str
        _function: _t.Callable[..., _t.Tuple[_Result, ...]]
        _functions: _t.Tuple[_t.Callable[..., _Result], ...]
        _line_number: int
        _line_offset: int

        __slots__ = ('_file_path', '_function', '_functions', '_line_number',
                     '_line_offset')

        def __new__(cls,
                    *functions: _t.Callable[_Params, _Result],
                    file_path: str = __file__,
                    line_number: int = 0,
                    line_offset: int = 0) -> 'Cleavage[_Result]':
            self = super().__new__(cls)
            self._functions = functions
            self._file_path = file_path
            self._line_number = line_number
            self._line_offset = line_offset
            self._function = _cleave(*functions,
                                     function_name='cleavage',
                                     file_path=file_path,
                                     line_number=line_number,
                                     line_offset=line_offset)
            return self

        def __call__(self,
                     *args: _Params.args,
                     **kwargs: _Params.kwargs) -> _t.Tuple[_Result, ...]:
            return self._function(*args, **kwargs)

        def __getnewargs_ex__(self) -> _t.Tuple[_t.Tuple[_t.Any, ...],
                                                _t.Dict[str, _t.Any]]:
            return self._functions, {'file_path': self._file_path,
                                     'line_number': self._line_number,
                                     'line_offset': self._line_offset}

        def __getstate__(self) -> None:
            return None

        def __setstate__(self, _state: None) -> None:
            pass

        __repr__ = generate_repr(__new__,
                                 field_seeker=seekers.complex_)
else:
    @final
    class Cleavage(_t.Generic[_Params, _Result]):
        _file_path: str
        _function: _t.Callable[_Params, _t.Tuple[_Result, ...]]
        _functions: _t.Tuple[_t.Callable[_Params, _Result], ...]
        _line_number: int
        _line_offset: int

        __slots__ = ('_file_path', '_function', '_functions', '_line_number',
                     '_line_offset')

        def __new__(cls,
                    *functions: _t.Callable[_Params, _Result],
                    file_path: str = __file__,
                    line_number: int = 0,
                    line_offset: int = 0) -> 'Cleavage[_Params, _Result]':
            self = super().__new__(cls)
            self._functions = functions
            self._file_path = file_path
            self._line_number = line_number
            self._line_offset = line_offset
            self._function = _cleave(*functions,
                                     function_name='cleavage',
                                     file_path=file_path,
                                     line_number=line_number,
                                     line_offset=line_offset)
            return self

        def __call__(self,
                     *args: _Params.args,
                     **kwargs: _Params.kwargs) -> _t.Tuple[_Result, ...]:
            return self._function(*args, **kwargs)

        def __getnewargs_ex__(self) -> _t.Tuple[_t.Tuple[_t.Any, ...],
                                                _t.Dict[str, _t.Any]]:
            return self._functions, {'file_path': self._file_path,
                                     'line_number': self._line_number,
                                     'line_offset': self._line_offset}

        def __getstate__(self) -> None:
            return None

        def __setstate__(self, _state: None) -> None:
            pass

        __repr__ = generate_repr(__new__,
                                 field_seeker=seekers.complex_)


@final
class Flip(_t.Generic[_Result]):
    @classmethod
    def from_function(
            cls, _function: _t.Union[Cleavage, Composition, Constant,
                                     'Flip[_Result]',
                                     _t.Callable[_Params, _Result]]
    ) -> _t.Union[Cleavage, Composition, Constant, 'Flip[_Result]',
                  _t.Callable[_Params, _Result]]:
        return (_function._function
                if isinstance(_function, cls)
                else (Composition(*_function._functions[:-1],
                                  cls.from_function(_function._functions[-1]),
                                  file_path=_function._file_path,
                                  line_number=_function._line_number,
                                  line_offset=_function._line_offset)
                      if isinstance(_function, Composition)
                      else (Cleavage(*[cls.from_function(function)
                                       for function in _function._functions],
                                     file_path=_function._file_path,
                                     line_number=_function._line_number,
                                     line_offset=_function._line_offset)
                            if isinstance(_function, Cleavage)
                            else (_function
                                  if isinstance(_function, Constant)
                                  else cls(_function)))))

    _function: _t.Callable[..., _Result]

    __slots__ = '_function',

    def __new__(cls, _function: _t.Callable[..., _Result]) -> 'Flip[_Result]':
        if isinstance(_function, cls):
            raise ValueError('Repeated flip should return original function.')
        self = super().__new__(cls)
        self._function = _function
        return self

    def __call__(self, *args: _Arg, **kwargs: _KwArg) -> _Result:
        return self._function(*args[::-1], **kwargs)

    def __getnewargs__(self) -> _t.Tuple[_t.Any, ...]:
        return (self._function,)

    __repr__ = generate_repr(__new__)


def _cleave(
        *functions: _t.Callable[_Params, _Result],
        function_name: str,
        file_path: str,
        line_number: int,
        line_offset: int,
        args_name: str = 'args',
        kwargs_name: str = 'kwargs'
) -> _t.Callable[_Params, _t.Tuple[_Result, ...]]:
    functions_names = [_function_to_unique_name(function)
                       for function in functions]
    result_node = ast.Tuple(
            [
                ast.Call(ast.Name(function_name, ast.Load(),
                                  lineno=line_number,
                                  col_offset=line_offset),
                         [ast.Starred(ast.Name(args_name, ast.Load(),
                                               lineno=line_number,
                                               col_offset=line_offset),
                                      ast.Load(),
                                      lineno=line_number,
                                      col_offset=line_offset)],
                         [ast.keyword(None, ast.Name(kwargs_name, ast.Load(),
                                                     lineno=line_number,
                                                     col_offset=line_offset),
                                      lineno=line_number,
                                      col_offset=line_offset)],
                         lineno=line_number,
                         col_offset=line_offset)
                for function_name in functions_names
            ],
            ast.Load(),
            lineno=line_number,
            col_offset=line_offset
    )
    function_definition_node = ast.FunctionDef(
            function_name,
            _to_signature_node(
                    variadic_positional_parameter=ast.arg(
                            args_name, None,
                            lineno=line_number,
                            col_offset=line_offset
                    ),
                    variadic_keyword_parameter=ast.arg(kwargs_name, None,
                                                       lineno=line_number,
                                                       col_offset=line_offset)
            ),
            [ast.Return(result_node,
                        lineno=line_number,
                        col_offset=line_offset)],
            [], None,
            lineno=line_number,
            col_offset=line_offset
    )
    return _compile_function(function_definition_node,
                             file_path=file_path,
                             namespace=dict(zip(functions_names, functions)))


def _combine(*maps: _t.Callable[[_T], _Result],
             function_name: str,
             file_path: str,
             line_number: int,
             line_offset: int) -> _t.Callable[..., _t.Tuple[_Result, ...]]:
    maps_names = [_function_to_unique_name(map_) for map_ in maps]
    args_names = [f'_arg{index}' for index in range(len(maps))]
    function_definition_node = ast.FunctionDef(
            function_name,
            _to_signature_node([ast.arg(arg_name, None,
                                        lineno=line_number,
                                        col_offset=line_offset)
                                for arg_name in args_names]),
            [ast.Return(ast.Tuple([ast.Call(ast.Name(map_name, ast.Load(),
                                                     lineno=line_number,
                                                     col_offset=line_offset),
                                            [ast.Name(arg_name, ast.Load(),
                                                      lineno=line_number,
                                                      col_offset=line_offset)],
                                            [],
                                            lineno=line_number,
                                            col_offset=line_offset)
                                   for map_name, arg_name in zip(maps_names,
                                                                 args_names)],
                                  ast.Load(),
                                  lineno=line_number,
                                  col_offset=line_offset),
                        lineno=line_number,
                        col_offset=line_offset)],
            [], None,
            lineno=line_number,
            col_offset=line_offset
    )
    return _compile_function(function_definition_node,
                             file_path=file_path,
                             namespace=dict(zip(maps_names, maps)))


def _compose(*functions: _t.Callable[..., _t.Any],
             function_name: str,
             file_path: str,
             line_number: int,
             line_offset: int,
             args_name: str = 'args',
             kwargs_name: str = 'kwargs') -> _t.Callable[..., _Result]:
    functions_names = [_function_to_unique_name(function)
                       for function in functions]

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
    calls_node = ast.Call(to_name_node(next(reversed_functions_names)),
                          [ast.Starred(to_name_node(args_name), ast.Load(),
                                       lineno=line_number,
                                       col_offset=line_offset)],
                          [ast.keyword(None, to_name_node(kwargs_name),
                                       lineno=line_number,
                                       col_offset=line_offset)],
                          lineno=line_number,
                          col_offset=line_offset)
    calls_node = functools.reduce(to_next_call_node,
                                  reversed_functions_names,
                                  calls_node)
    function_definition_node = ast.FunctionDef(
            function_name,
            _to_signature_node(
                    variadic_positional_parameter=ast.arg(
                            args_name, None,
                            lineno=line_number,
                            col_offset=line_offset
                    ),
                    variadic_keyword_parameter=ast.arg(kwargs_name, None,
                                                       lineno=line_number,
                                                       col_offset=line_offset)
            ),
            [ast.Return(calls_node,
                        lineno=line_number,
                        col_offset=line_offset)],
            [],
            None,
            lineno=line_number,
            col_offset=line_offset
    )
    return _compile_function(function_definition_node,
                             file_path=file_path,
                             namespace=dict(zip(functions_names, functions)))


def _compile_function(
        function_definition_node: ast.FunctionDef,
        *,
        file_path: str,
        namespace: _t.Dict[str, _t.Any],
        module_factory: _t.Callable[..., ast.Module] =
        ast.Module
        if sys.version_info < (3, 8)
        # Python3.8 adds `type_ignores` parameter
        else _t.cast(_t.Callable[..., ast.Module],
                     functools.partial(ast.Module,
                                       type_ignores=[]))
) -> _t.Callable[..., _t.Any]:
    tree = module_factory([function_definition_node])
    code = compile(tree, file_path, 'exec')
    exec(code, namespace)
    return namespace[function_definition_node.name]


if sys.version_info < (3, 8):
    def _to_signature_node(
            positional_only_parameters: _t.Optional[_t.List[ast.arg]] = None,
            positional_or_keyword_parameters: _t.Optional[_t.List[ast.arg]]
            = None,
            variadic_positional_parameter: _t.Optional[ast.arg] = None,
            keyword_only_parameters: _t.Optional[_t.List[ast.arg]] = None,
            variadic_keyword_parameter: _t.Optional[ast.arg] = None,
            positionals_defaults: _t.Optional[_t.List[ast.expr]] = None,
            keywords_defaults: _t.Optional[_t.List[_t.Optional[ast.expr]]]
            = None
    ) -> ast.arguments:
        return ast.arguments((positional_only_parameters or [])
                             + (positional_or_keyword_parameters or []),
                             variadic_positional_parameter,
                             keyword_only_parameters or [],
                             keywords_defaults or [],
                             variadic_keyword_parameter,
                             positionals_defaults or [])
else:
    def _to_signature_node(
            positional_only_parameters: _t.Optional[_t.List[ast.arg]] = None,
            positional_or_keyword_parameters: _t.Optional[_t.List[ast.arg]]
            = None,
            variadic_positional_parameter: _t.Optional[ast.arg] = None,
            keyword_only_parameters: _t.Optional[_t.List[ast.arg]] = None,
            variadic_keyword_parameter: _t.Optional[ast.arg] = None,
            positionals_defaults: _t.Optional[_t.List[ast.expr]] = None,
            keywords_defaults: _t.Optional[_t.List[_t.Optional[ast.expr]]]
            = None
    ) -> ast.arguments:
        return ast.arguments(positional_only_parameters or [],
                             positional_or_keyword_parameters or [],
                             variadic_positional_parameter,
                             keyword_only_parameters or [],
                             keywords_defaults or [],
                             variadic_keyword_parameter,
                             positionals_defaults or [])


def _function_to_unique_name(function: _t.Callable[..., _t.Any]) -> str:
    # we are not using `__name__`/`__qualname__` attributes
    # due to their potential non-uniqueness
    return '_' + str(id(function)).replace('-', '_')


@to_signature.register(Cleavage)
def _(_value: Cleavage) -> Signature:
    return to_signature(_value._functions[0])


@to_signature.register(Combination)
def _(_value: Combination) -> Signature:
    return to_signature(_value._function)


@to_signature.register(Composition)
def _(_value: Composition) -> Signature:
    last_signature = to_signature(_value._functions[0])
    returns = (_t.Union[tuple(signature.returns
                              for signature in last_signature.signatures
                              if signature.expects(None))]
               if isinstance(last_signature, OverloadedSignature)
               else last_signature.returns)
    return _replace_returns(to_signature(_value._functions[-1]), returns)


@functools.singledispatch
def _replace_returns(signature: Signature, returns: _t.Any) -> Signature:
    raise TypeError(type(signature))


@_replace_returns.register(OverloadedSignature)
def _(signature: OverloadedSignature, returns: _t.Any) -> Signature:
    return OverloadedSignature(*[_replace_returns(sub_signature, returns)
                                 for sub_signature in signature.signatures])


@_replace_returns.register(PlainSignature)
def _(signature: PlainSignature, returns: _t.Any) -> Signature:
    return PlainSignature(*signature.parameters,
                          returns=returns)


@to_signature.register(Constant)
def _(_value: Constant) -> Signature:
    return to_signature(_value.__call__)


@to_signature.register(Curry)
def _(_value: Curry) -> Signature:
    return _value._signature


@to_signature.register(Flip)
def _(_value: Flip) -> Signature:
    return to_signature(_value._function)
