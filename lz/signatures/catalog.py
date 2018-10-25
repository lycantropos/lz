import importlib
import inspect
import pathlib
import struct
import types
from collections import deque
from functools import singledispatch
from types import (BuiltinMethodType,
                   FunctionType,
                   ModuleType)
from typing import (Any,
                    Optional,
                    Union)

from lz import right
from lz.functional import compose
from .file_system import INIT_MODULE_NAME
from .hints import (MethodDescriptorType,
                    WrapperDescriptorType)
from .utils import cached_map


class Path:
    SEPARATOR = '.'

    def __init__(self, *parts: str) -> None:
        self.parts = parts

    def __str__(self) -> str:
        return self.SEPARATOR.join(self.parts)

    def __repr__(self) -> str:
        return (type(self).__qualname__
                + '(' + ', '.join(map(repr, self.parts)) + ')')

    def __eq__(self, other: 'Path') -> bool:
        if not isinstance(other, Path):
            return NotImplemented
        return self.parts == other.parts

    def __hash__(self) -> int:
        return hash(self.parts)

    def join(self, other: 'Path') -> 'Path':
        if not isinstance(other, Path):
            return NotImplemented
        return type(self)(*self.parts, *other.parts)

    @property
    def parent(self) -> 'Path':
        return type(self)(*self.parts[:-1])

    def with_parent(self, parent: 'Path') -> 'Path':
        return type(self)(*parent.parts, *self.parts[len(parent.parts):])

    def is_child_of(self, parent: 'Path') -> bool:
        return self.parts[:len(parent.parts)] == parent.parts


WILDCARD_IMPORT = Path('*')


@singledispatch
def factory(object_: Any) -> Path:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


def is_propertyspace(object_: Any) -> bool:
    return isinstance(object_, (ModuleType, type))


@factory.register(BuiltinMethodType)
@factory.register(FunctionType)
@factory.register(MethodDescriptorType)
@factory.register(WrapperDescriptorType)
@factory.register(type)
def from_class_or_function(object_: Union[BuiltinMethodType, FunctionType,
                                          MethodDescriptorType, type]
                           ) -> Path:
    module = importlib.import_module(module_name_factory(object_))
    propertyspaces = deque([(Path(), module)])
    while propertyspaces:
        parent_path, propertyspace = propertyspaces.pop()
        to_path = compose(parent_path.join, factory)
        namespace = dict(vars(propertyspace))
        try:
            return next(to_path(name)
                        for name, content in namespace.items()
                        if content is object_)
        except StopIteration:
            propertyspaces.extendleft(((to_path(name), content)
                                       for name, content in namespace.items()
                                       if is_propertyspace(content)))
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


names_replacements = {'Protocol': '_Protocol'}


@factory.register(str)
def from_string(string: str) -> Path:
    parts = string.split(Path.SEPARATOR)
    parts = map(names_replacements.get, parts, parts)
    return Path(*parts)


@singledispatch
def module_name_factory(object_: Any) -> str:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


replacements = {'nt': 'os',
                'posix': 'os'}


@module_name_factory.register(str)
def module_name_from_string(object_: str) -> str:
    return replacements.get(object_, object_)


@module_name_factory.register(BuiltinMethodType)
@module_name_factory.register(FunctionType)
@module_name_factory.register(type)
@cached_map({struct.Struct: struct.__name__,
             types.FrameType: types.__name__})
def module_name_from_class_or_function(object_: Union[BuiltinMethodType,
                                                      FunctionType, type]
                                       ) -> str:
    result = object_.__module__
    if result is None:
        result = object_.__self__.__class__.__module__
    return module_name_factory(result)


@module_name_factory.register(MethodDescriptorType)
@module_name_factory.register(WrapperDescriptorType)
def module_name_from_method_descriptor(object_: MethodDescriptorType) -> str:
    return module_name_factory(object_.__objclass__)
