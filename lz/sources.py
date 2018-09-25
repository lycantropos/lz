import importlib
import inspect
import sys
from collections import namedtuple
from functools import singledispatch
from pathlib import Path
from types import ModuleType
from typing import (Iterable,
                    Tuple)

import typeshed

from . import catalog
from .file_system import (INIT_MODULE_NAME,
                          find_files)
from .functional import (combine,
                         compose,
                         identity,
                         unpack)
from .hints import Map
from .iterating import (copier,
                        flatmapper,
                        mapper,
                        sifter)

STUB_EXTENSION = '.pyi'


@singledispatch
def factory(module: ModuleType) -> Path:
    result = Path(inspect.getfile(module))
    if result.with_suffix('').name == INIT_MODULE_NAME:
        result = result.parent
    return result


@factory.register(catalog.Path)
def from_module_path(path: catalog.Path) -> Path:
    try:
        result = cache[path]
    except KeyError:
        module = importlib.import_module(str(path))
        result = factory(module)
        cache[path] = result
    return result


def generate_stubs_cache_items(root: Path
                               ) -> Iterable[Tuple[catalog.Path, Path]]:
    Version = namedtuple('Version', ['major', 'minor'])

    def is_supported_version_directory(directory: Path) -> bool:
        system_version = get_system_version()
        return any(version.major == system_version.major
                   and version.minor <= system_version.minor
                   for version in to_versions(directory))

    def to_versions(directory: Path,
                    *,
                    major_versions_separator: str = 'and'
                    ) -> Iterable[Version]:
        raw_versions = directory.name.split(major_versions_separator)

        def to_version(raw_version: str,
                       *,
                       version_parts_separator: str = '.') -> Version:
            raw_version_parts = raw_version.split(version_parts_separator)
            version_parts = list(map(int, raw_version_parts))
            try:
                major, minor = version_parts
            except ValueError:
                major, = version_parts
                minor = 0
            return Version(major, minor)

        yield from map(to_version, raw_versions)

    def get_system_version() -> Version:
        major, minor, *_ = sys.version_info
        return Version(major, minor)

    def module_full_name_factory(directory: Path) -> Map[Path, catalog.Path]:
        def to_module_path(stub: Path) -> catalog.Path:
            relative_stub_path = stub.relative_to(directory)
            return catalog.factory(relative_stub_path.with_suffix('.py'))

        return to_module_path

    def to_directory_items(directory: Path
                           ) -> Iterable[Tuple[catalog.Path, Path]]:
        to_module_full_name = module_full_name_factory(directory)
        finder = compose(unpack(zip),
                         combine(mapper(to_module_full_name), identity),
                         copier(2),
                         sifter(is_stub),
                         find_files)
        yield from finder(directory)

    to_directories_items = compose(flatmapper(to_directory_items),
                                   sifter(is_supported_version_directory),
                                   sifter(Path.is_dir))
    yield from to_directories_items(root.iterdir())


def is_stub(path: Path) -> bool:
    return path.suffixes == [STUB_EXTENSION]


cache = dict(generate_stubs_cache_items(factory(typeshed) / 'stdlib'))
