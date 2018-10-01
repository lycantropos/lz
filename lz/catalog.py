import inspect
import pathlib
from functools import singledispatch
from types import (BuiltinMethodType,
                   FunctionType,
                   ModuleType)
from typing import (Any,
                    Optional,
                    Union)

from . import right
from .file_system import INIT_MODULE_NAME
from .hints import MethodDescriptorType


class Path:
    SEPARATOR = '.'

    def __init__(self, *parts: str) -> None:
        self.parts = parts

    def __repr__(self) -> str:
        return self.SEPARATOR.join(self.parts)

    def __lt__(self, other: 'Path') -> bool:
        if not isinstance(other, Path):
            return NotImplemented
        return self.parts < other.parts

    def __eq__(self, other: 'Path') -> bool:
        if not isinstance(other, Path):
            return NotImplemented
        return self.parts == other.parts

    def __hash__(self) -> int:
        return hash(self.parts)

    def __bool__(self) -> bool:
        return bool(self.parts)

    def join(self, other: Union[str, 'Path']) -> 'Path':
        if isinstance(other, str):
            return Path(*self.parts, other)
        elif isinstance(other, Path):
            return Path(*self.parts, *other.parts)
        return NotImplemented

    @property
    def parent(self) -> 'Path':
        return Path(*self.parts[:-1])


WILDCARD_IMPORT = Path('*')


@singledispatch
def factory(object_: Any) -> Path:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


@factory.register(BuiltinMethodType)
@factory.register(FunctionType)
@factory.register(MethodDescriptorType)
@factory.register(type)
def from_class_or_function(object_: Union[BuiltinMethodType, FunctionType,
                                          MethodDescriptorType, type]
                           ) -> Path:
    return factory(object_.__qualname__)


@factory.register(ModuleType)
def from_module(object_: ModuleType) -> Path:
    return factory(object_.__name__)


@factory.register(pathlib.Path)
def from_relative_file_path(path: pathlib.Path) -> Path:
    if path.is_absolute():
        raise ValueError('Path should be relative.')
    *parts, module_file_name = path.parts

    def to_module_name(file_name: str) -> Optional[str]:
        if file_name == '.':
            return None
        result = inspect.getmodulename(file_name)
        if result == INIT_MODULE_NAME:
            return None
        return result

    module_name = to_module_name(module_file_name)
    if module_name is not None:
        parts = right.attacher(module_name)(parts)
    return Path(*parts)


@factory.register(str)
def from_string(string: str) -> Path:
    return Path(*string.split(Path.SEPARATOR))


@singledispatch
def module_name_factory(object_: Any) -> str:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


@module_name_factory.register(BuiltinMethodType)
@module_name_factory.register(FunctionType)
@module_name_factory.register(type)
def module_name_from_class_or_function(object_: Union[BuiltinMethodType,
                                                      FunctionType, type]
                                       ) -> str:
    result = object_.__module__
    if result is None:
        result = object_.__self__.__class__.__module__
    return result


@module_name_factory.register(MethodDescriptorType)
def module_name_from_method_descriptor(object_: MethodDescriptorType) -> str:
    return module_name_factory(object_.__objclass__)


@module_name_factory.register(ModuleType)
def module_name_from_module(object_: ModuleType) -> str:
    return object_.__name__
