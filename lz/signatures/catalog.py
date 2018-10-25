import importlib
import inspect
import pathlib
import struct
import sys
import types
from functools import singledispatch
from itertools import chain
from types import (BuiltinMethodType,
                   FunctionType,
                   ModuleType)
from typing import (Any,
                    Iterable,
                    Optional,
                    Union)

from lz import right
from lz.functional import compose
from lz.iterating import expand
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


@singledispatch
def paths_factory(object_: Any) -> Iterable[Path]:
    yield factory(object_)


@paths_factory.register(BuiltinMethodType)
@paths_factory.register(FunctionType)
@paths_factory.register(MethodDescriptorType)
@paths_factory.register(WrapperDescriptorType)
@paths_factory.register(type)
def paths_from_class_or_function(object_: Union[BuiltinMethodType,
                                                FunctionType,
                                                MethodDescriptorType, type]
                                 ) -> Iterable[Path]:
    module = importlib.import_module(module_name_factory(object_))
    propertyspaces = iter(expand((Path(), module)))
    while True:
        try:
            parent_path, propertyspace = next(propertyspaces)
        except StopIteration:
            break
        to_path = compose(parent_path.join, factory)
        namespace = dict(vars(propertyspace))
        yield from (to_path(name)
                    for name, content in namespace.items()
                    if content is object_)
        propertyspaces = chain(propertyspaces,
                               ((to_path(name), content)
                                for name, content in namespace.items()
                                if is_propertyspace(content)))
    yield from paths_factory(object_.__qualname__)


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


module_name_from_class_or_function_cache = {
    struct.Struct: struct.__name__,
    types.CodeType: types.__name__,
    types.FrameType: types.__name__,
    types.ModuleType: types.__name__,
}

if sys.version_info >= (3, 7):
    import contextvars

    module_name_from_class_or_function_cache.update(
            {contextvars.Context: contextvars.__name__,
             contextvars.ContextVar: contextvars.__name__,
             contextvars.Token: contextvars.__name__,
             types.TracebackType: types.__name__})


@module_name_factory.register(BuiltinMethodType)
@module_name_factory.register(FunctionType)
@module_name_factory.register(type)
@cached_map(module_name_from_class_or_function_cache)
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
