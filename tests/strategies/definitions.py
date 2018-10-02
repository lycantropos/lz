import _collections_abc
import _hashlib
import _io
import _json
import _string
import _thread
import codecs
import collections
import ctypes.util
import faulthandler
import inspect
import os
import socket
import struct
import sys
import types
import zipimport
from operator import methodcaller
from pathlib import Path
from types import (BuiltinFunctionType,
                   ModuleType)
from typing import (Any,
                    Iterable,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from lz.signatures.hints import MethodDescriptorType


def find_stdlib_modules_names(directory_path: Path = Path(os.__file__).parent,
                              ) -> Iterable[str]:
    yield from sys.builtin_module_names

    def is_stdlib_module_path(path: Path) -> bool:
        file_name = path.name
        # skips '__pycache__', 'site-packages', etc.
        return not (file_name.startswith('__') and file_name.endswith('__')
                    or '-' in file_name)

    sources_paths = filter(is_stdlib_module_path, directory_path.iterdir())
    sources_relative_paths = map(methodcaller(Path.relative_to.__name__,
                                              directory_path),
                                 sources_paths)
    yield from map(str, map(methodcaller(Path.with_suffix.__name__, ''),
                            sources_relative_paths))


stdlib_modules_names = frozenset(find_stdlib_modules_names())
stdlib_modules = {module
                  for module_name, module in sys.modules.items()
                  if module_name in stdlib_modules_names}
supported_modules = (stdlib_modules
                     # support for these stdlib modules is not found
                     # in ``typeshed`` package
                     - {_string,
                        ctypes,
                        faulthandler})

is_module_supported = supported_modules.__contains__

modules = (strategies.sampled_from(list(stdlib_modules))
           .filter(is_module_supported))


def flatten(object_: Union[ModuleType, type]) -> SearchStrategy:
    return strategies.sampled_from(list(vars(object_).values()))


def is_object_supported(object_: Any) -> bool:
    return (not isinstance(object_, ModuleType)
            or is_module_supported(object_))


objects = modules.flatmap(flatten)


def is_not_private(object_: Union[BuiltinFunctionType,
                                  MethodDescriptorType,
                                  type]) -> bool:
    return not object_.__name__.startswith('_')


unsupported_classes = {_thread.LockType,
                       _thread.RLock,
                       _collections_abc.mappingproxy,
                       _collections_abc.dict_keys,
                       _collections_abc.dict_items,
                       _hashlib.HASH,
                       types.FrameType}


def is_class_supported(class_: type) -> bool:
    return class_ not in unsupported_classes


classes = (objects.filter(inspect.isclass)
           .filter(is_class_supported)
           .filter(is_not_private))
classes_objects = classes.flatmap(flatten)
methods = classes_objects.filter(inspect.isfunction)


def is_method_descriptor(object_: Any) -> bool:
    return isinstance(object_, MethodDescriptorType)


unsupported_methods_descriptors = {dict.get,
                                   int.conjugate,
                                   float.conjugate,
                                   zipimport.zipimporter.find_loader,
                                   _io.BufferedRWPair.peek,
                                   _collections_abc.generator.send,
                                   _collections_abc.generator.throw,
                                   _collections_abc.generator.close,
                                   _collections_abc.coroutine.send,
                                   _collections_abc.coroutine.throw,
                                   _collections_abc.coroutine.close,
                                   collections.OrderedDict.clear,
                                   collections.OrderedDict.pop,
                                   collections.OrderedDict.update,
                                   collections.OrderedDict.setdefault,
                                   struct.Struct.pack,
                                   struct.Struct.unpack,
                                   struct.Struct.unpack_from,
                                   struct.Struct.iter_unpack,
                                   struct.Struct.pack_into}
if sys.version_info >= (3, 6):
    unsupported_methods_descriptors.update(
            {_collections_abc.async_generator.asend,
             _collections_abc.async_generator.athrow,
             _collections_abc.async_generator.aclose})
    if sys.platform == 'linux':
        unsupported_methods_descriptors.add(socket.socket.sendmsg_afalg)
if sys.version_info >= (3, 7):
    unsupported_methods_descriptors.update({bytearray.isascii,
                                            bytes.isascii,
                                            str.isascii,
                                            socket.socket.getblocking})
if sys.platform == 'win32':
    unsupported_methods_descriptors.add(socket.socket.share)


def is_method_descriptor_supported(method_descriptor: MethodDescriptorType
                                   ) -> bool:
    return method_descriptor not in unsupported_methods_descriptors


methods_descriptors = (classes_objects.filter(is_method_descriptor)
                       .filter(is_not_private)
                       .filter(is_method_descriptor_supported))
functions = objects.filter(inspect.isfunction)

# support for these built-in functions in ``typeshed`` package is not found
unsupported_built_in_functions = {_hashlib.openssl_sha1,
                                  _hashlib.openssl_sha224,
                                  _hashlib.openssl_sha256,
                                  _hashlib.openssl_sha384,
                                  _hashlib.openssl_sha512,
                                  _hashlib.openssl_md5,
                                  _json.encode_basestring,
                                  socket.dup,
                                  sys.callstats,
                                  sys.getallocatedblocks,
                                  sys.set_coroutine_wrapper,
                                  sys.get_coroutine_wrapper,
                                  _thread.start_new_thread,
                                  _thread.allocate,
                                  _thread.exit_thread,
                                  _thread.interrupt_main,
                                  _thread.stack_size,
                                  os.get_inheritable,
                                  os.set_inheritable,
                                  # FIXME: next functions meta-info
                                  # seems to be broken
                                  codecs.strict_errors,
                                  codecs.ignore_errors,
                                  codecs.replace_errors,
                                  codecs.xmlcharrefreplace_errors,
                                  codecs.backslashreplace_errors,
                                  codecs.namereplace_errors}
if sys.version_info >= (3, 6):
    unsupported_built_in_functions.update({sys.getfilesystemencodeerrors,
                                           sys.set_asyncgen_hooks,
                                           sys.get_asyncgen_hooks})
if sys.platform == 'win32':
    unsupported_built_in_functions.update({os.get_handle_inheritable,
                                           os.set_handle_inheritable})


def is_function_supported(function: BuiltinFunctionType) -> bool:
    return function not in unsupported_built_in_functions


def has_module(function: BuiltinFunctionType) -> bool:
    return bool(function.__module__)


built_in_functions = (objects.filter(inspect.isbuiltin)
                      .filter(has_module)
                      .filter(is_not_private)
                      .filter(is_function_supported))
