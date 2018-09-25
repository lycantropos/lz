import importlib
import inspect
import pathlib
from functools import singledispatch
from operator import methodcaller
from types import (BuiltinMethodType,
                   FunctionType,
                   MethodDescriptorType,
                   ModuleType)
from typing import (Any,
                    Dict,
                    Optional,
                    Union)

from . import (dictionaries,
               left,
               right)
from .file_system import INIT_MODULE_NAME
from .functional import (compose,
                         unpack)
from .iterating import mapper


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

    def join(self, part: str) -> 'Path':
        return Path(*self.parts, part)


Paths = Dict[Path, Any]


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
@module_name_factory.register(MethodDescriptorType)
@module_name_factory.register(type)
def module_name_from_non_module(object_: Union[BuiltinMethodType,
                                               FunctionType,
                                               MethodDescriptorType, type]
                                ) -> str:
    result = object_.__module__
    if result is None:
        result = object_.__self__.__class__.__module__
    return result


@module_name_factory.register(ModuleType)
def module_name_from_module(object_: ModuleType) -> str:
    return object_.__name__


@singledispatch
def paths_factory(object_: Any,
                  *,
                  parent_path: Path) -> Paths:
    return {parent_path: object_}


@paths_factory.register(Path)
def paths_from_module_path(object_: Path,
                           *,
                           parent_path: Path) -> Paths:
    module = importlib.import_module(str(object_))
    return paths_factory(module,
                         parent_path=parent_path)


@paths_factory.register(FunctionType)
@paths_factory.register(ModuleType)
@paths_factory.register(type)
def paths_from_class_or_function(object_: Union[ModuleType, type],
                                 *,
                                 parent_path: Path) -> Paths:
    def to_sub_paths(name: str, content: Any) -> Paths:
        return paths_factory(content,
                             parent_path=parent_path.join(name))

    to_paths = compose(dictionaries.merge,
                       left.attacher({parent_path: object_}),
                       mapper(unpack(to_sub_paths)),
                       methodcaller('items'),
                       vars)
    return to_paths(object_)
