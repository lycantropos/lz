import io
import os
import pkgutil
import sys
from functools import partial
from typing import (Any,
                    Dict,
                    Hashable,
                    Iterable,
                    TextIO)

import pytest
from hypothesis import (HealthCheck,
                        settings)

from lz.replication import (replicate,
                            replicate_iterable)

base_directory_path = os.path.dirname(__file__)
sys.path.append(base_directory_path)


def explore_pytest_plugins(package_path: str) -> Iterable[str]:
    directories = find_directories(package_path)
    packages_paths = [
        file_finder.path
        for file_finder, _, is_package in pkgutil.iter_modules(directories)
        if not is_package]
    if not packages_paths:
        return
    common_path = os.path.dirname(os.path.commonpath(packages_paths))
    for module_info in pkgutil.iter_modules(packages_paths):
        file_finder, module_name, is_package = module_info
        if is_package:
            continue
        package_path = os.path.relpath(file_finder.path,
                                       start=common_path)
        package_name = path_to_module_name(package_path)
        yield '{package}.{module}'.format(package=package_name,
                                          module=module_name)


def find_directories(root: str) -> Iterable[str]:
    if not os.path.isdir(root):
        return
    yield root
    for root, sub_directories, _ in os.walk(root):
        yield from map(partial(os.path.join, root),
                       sub_directories)


def path_to_module_name(path: str) -> str:
    if os.path.isabs(path):
        err_msg = ('Invalid path: "{path}", '
                   'should be relative.'
                   .format(path=path))
        raise ValueError(err_msg)
    return os.path.normpath(path).replace(os.sep, '.')


fixtures_package_path = os.path.join(base_directory_path, 'fixtures')
pytest_plugins = list(explore_pytest_plugins(fixtures_package_path))

settings.register_profile('default',
                          deadline=None,
                          max_examples=10,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])


@pytest.fixture(scope='session',
                autouse=True)
def patch_sized_replication() -> None:
    def replicate_byte_buffer(object_: io.BytesIO,
                              *,
                              count: int) -> Iterable[io.BytesIO]:
        yield from map(io.BytesIO, replicate(object_.getvalue(),
                                             count=count))

    replicate.register(io.BytesIO, replicate_byte_buffer)

    def replicate_byte_stream(object_: io.BufferedReader,
                              *,
                              count: int) -> Iterable[io.BufferedReader]:
        yield from map(io.BufferedReader, replicate(object_.raw,
                                                    count=count))

    replicate.register(io.BufferedReader, replicate_byte_stream)

    def replicate_text_stream(object_: TextIO,
                              *,
                              count: int) -> Iterable[TextIO]:
        yield from map(partial(io.TextIOWrapper,
                               encoding=object_.encoding),
                       replicate(object_.buffer,
                                 count=count))

    replicate.register(io.TextIOWrapper, replicate_text_stream)

    def replicate_sized(object_: Any,
                        *,
                        count: int) -> Iterable[Any]:
        yield from map(type(object_), replicate_iterable(object_,
                                                         count=count))

    replicate.register(bytearray, replicate_sized)
    replicate.register(frozenset, replicate_sized)
    replicate.register(list, replicate_sized)
    replicate.register(set, replicate_sized)
    replicate.register(tuple, replicate_sized)

    def replicate_dictionary(object_: Dict[Hashable, Any],
                             *,
                             count: int) -> Iterable[Dict[Hashable, Any]]:
        yield from map(dict, replicate_iterable(object_.items(),
                                                count=count))

    replicate.register(dict, replicate_dictionary)
