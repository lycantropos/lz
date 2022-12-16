import functools
import inspect
import itertools
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Iterable,
                    TypeVar,
                    overload)

from typing_extensions import ParamSpec

from ._core.functional import Cleavage, Combination, Composition, Constant, \
    Curry
from ._core.signatures import (Signature,
                               to_signature)
from .hints import (Domain,
                    Range)


def identity(argument: Domain) -> Domain:
    """
    Returns object itself.

    >>> identity(0)
    0
    """
    return argument


_Params = ParamSpec('_Params')
_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T3 = TypeVar('_T3')


@overload
def compose(_last_function: Callable[[_T2], _T3],
            _penult_function: Callable[_Params, _T2]) -> Callable[_Params, _T3]:
    ...


@overload
def compose(_last_function: Callable[[_T2], _T3],
            _penult_function: Callable[[_T1], _T2],
            _front_function: Callable[_Params, _T1]) -> Callable[_Params, _T3]:
    ...


def compose(_last_function: Callable[[_T2], _T3],
            _penult_function: Callable[..., _T2],
            *_rest_functions: Callable[..., Any]) -> Callable[_Params, _T3]:
    """
    Returns functions composition.

    >>> sum_of_first_n_natural_numbers = compose(sum, range)
    >>> sum_of_first_n_natural_numbers(10)
    45
    """
    caller_frame_info = inspect.stack()[1]
    return Composition(_last_function, _penult_function, *_rest_functions,
                       file_path=caller_frame_info.filename,
                       line_number=caller_frame_info.lineno,
                       line_offset=0)


@to_signature.register(Composition)
def _(object_: Composition) -> Signature:
    return to_signature(object_.functions[-1])


def combine(*maps: Callable) -> Callable[[Iterable[Domain]], Iterable[Range]]:
    """
    Returns function that applies each map to corresponding argument.

    >>> encoder_decoder = combine(str.encode, bytes.decode)
    >>> list(encoder_decoder(['hello', b'world']))
    [b'hello', 'world']
    """
    return Combination(*maps)


@to_signature.register(Combination)
def _(object_: Combination) -> Signature:
    return to_signature(object_.__call__)


@to_signature.register(Curry)
def _(object_: Curry) -> Signature:
    return object_.signature


def curry(function: Callable[..., Range]) -> Curry:
    """
    Returns curried version of given function.

    >>> curried_pow = curry(pow)
    >>> two_to_power = curried_pow(2)
    >>> two_to_power(10)
    1024
    """
    return Curry(function, to_signature(function))


def pack(
        function: Callable[_Params, Range]
) -> Callable[[_Params.args, _Params.kwargs], Range]:
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


def apply(function: Callable[_Params, Range],
          args: _Params.args,
          kwargs: _Params.kwargs = MappingProxyType({})) -> Range:
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


@to_signature.register(Constant)
def _(object_: Constant) -> Signature:
    return to_signature(object_.__call__)


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


@to_signature.register(Cleavage)
def _(object_: Cleavage) -> Signature:
    return to_signature(object_.functions[0])


def flatmap(function: Callable[[Domain], Iterable[Range]],
            *iterables: Iterable[Domain]) -> Iterable[Range]:
    """
    Applies given function to the arguments aggregated from given iterables
    and concatenates results into plain iterable.

    >>> list(flatmap(range, range(5)))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3]
    """
    yield from itertools.chain.from_iterable(map(function, *iterables))
