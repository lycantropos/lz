import functools as _functools
import inspect as _inspect
import itertools as _itertools
import types as _types
import typing as _t

import typing_extensions as _te

from ._core.functional import (Cleavage,
                               Combination,
                               Composition,
                               Constant,
                               Curry)
from ._core.signatures import to_signature as _to_signature

_Params = _te.ParamSpec('_Params')
_T3 = _t.TypeVar('_T3')
_T1 = _t.TypeVar('_T1')
_T2 = _t.TypeVar('_T2')


def identity(argument: _T1) -> _T1:
    """
    Returns object itself.

    >>> identity(0)
    0
    """
    return argument


def compose(
        _last_function: _t.Callable[[_T2], _T3],
        _penult_function: _t.Callable[..., _T2],
        *_rest_functions: _t.Callable[..., _t.Any]
) -> _t.Callable[_Params, _T3]:
    """
    Returns functions composition.

    >>> sum_of_first_n_natural_numbers = compose(sum, range)
    >>> sum_of_first_n_natural_numbers(10)
    45
    """
    caller_frame_info = _inspect.stack()[1]
    return Composition(_last_function, _penult_function, *_rest_functions,
                       file_path=caller_frame_info.filename,
                       line_number=caller_frame_info.lineno,
                       line_offset=0)


def combine(
        *maps: _t.Callable[[_T1], _T2]
) -> _t.Callable[[_t.Iterable[_T1]], _t.Iterable[_T2]]:
    """
    Returns function that applies each map to corresponding argument.

    >>> encoder_decoder = combine(str.encode, bytes.decode)
    >>> list(encoder_decoder(['hello', b'world']))
    [b'hello', 'world']
    """
    return Combination(*maps)


def curry(function: _t.Callable[..., _T2]) -> Curry:
    """
    Returns curried version of given function.

    >>> curried_pow = curry(pow)
    >>> two_to_power = curried_pow(2)
    >>> two_to_power(10)
    1024
    """
    return Curry(function, _to_signature(function))


def pack(function: _t.Callable[_Params, _T2]) -> _t.Callable[[_T1, _T2], _T2]:
    """
    Returns function that works with single iterable parameter
    by unpacking elements to given function.

    >>> packed_int = pack(int)
    >>> packed_int(['10'])
    10
    >>> packed_int(['10'], {'base': 2})
    2
    """
    return _functools.partial(apply, function)


def apply(function: _t.Callable[_Params, _T2],
          args: _Params.args,
          kwargs: _Params.kwargs = _types.MappingProxyType({})) -> _T2:
    """
    Calls given function with given positional and keyword arguments.
    """
    return function(*args, **kwargs)


def to_constant(object_: _T1) -> _t.Callable[..., _T1]:
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


def flip(function: _t.Callable[..., _T2]) -> _t.Callable[..., _T2]:
    """
    Returns function with positional arguments flipped.

    >>> flipped_power = flip(pow)
    >>> flipped_power(2, 4)
    16
    """
    return _functools.partial(call_flipped, function)


def call_flipped(function: _t.Callable[..., _T2],
                 *args: _T1,
                 **kwargs: _T1) -> _T2:
    """
    Calls given function with positional arguments flipped.
    """
    return function(*args[::-1], **kwargs)


def cleave(
        *functions: _t.Callable[..., _T1]
) -> _t.Callable[..., _t.Iterable[_T1]]:
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


def flatmap(function: _t.Callable[[_T1], _t.Iterable[_T2]],
            *iterables: _t.Iterable[_T1]) -> _t.Iterable[_T2]:
    """
    Applies given function to the arguments aggregated from given iterables
    and concatenates results into plain iterable.

    >>> list(flatmap(range, range(5)))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3]
    """
    yield from _itertools.chain.from_iterable(map(function, *iterables))
