import os
import pkgutil
import sys
from functools import partial
from typing import Iterator

from _pytest.config import Parser
from _pytest.python import Metafunc

base_directory_path = os.path.dirname(__file__)
sys.path.append(base_directory_path)


def explore_pytest_plugins(package_path: str) -> Iterator[str]:
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


def find_directories(root: str) -> Iterator[str]:
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


def pytest_addoption(parser: Parser) -> None:
    parser.addoption('--repeat',
                     action='store',
                     help='Number of times to repeat each test.')


def pytest_generate_tests(metafunc: Metafunc) -> None:
    if metafunc.config.option.repeat is None:
        return
    count = int(metafunc.config.option.repeat)
    # We're going to duplicate these tests by parametrisation,
    # which requires that each test has a fixture to accept the parameter.
    # We can add a new fixture like so:
    metafunc.fixturenames.append('tmp_ct')
    # Now we parametrize. This is what happens when we do e.g.,
    # @pytest.mark.parametrize('tmp_ct', range(count))
    # def test_foo(): pass
    metafunc.parametrize('tmp_ct', range(count))
