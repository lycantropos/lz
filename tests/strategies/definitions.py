import importlib
import inspect
import os
import platform
import sys
from operator import methodcaller
from pathlib import Path
from types import (BuiltinFunctionType,
                   ModuleType)
from typing import (Any,
                    Iterable,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from lz.signatures.hints import (MethodDescriptorType,
                                 WrapperDescriptorType)


def find_stdlib_modules_names(directory_path: Path = Path(os.__file__).parent,
                              ) -> Iterable[str]:
    yield from sys.builtin_module_names

    def is_stdlib_module_path(path: Path) -> bool:
        base_name = path.stem
        # skips 'LICENSE', '__pycache__', 'site-packages', etc.
        return not (base_name.isupper()
                    or base_name.startswith('__')
                    or '-' in base_name)

    sources_paths = filter(is_stdlib_module_path, directory_path.iterdir())
    sources_relative_paths = map(methodcaller(Path.relative_to.__name__,
                                              directory_path),
                                 sources_paths)
    yield from map(str, map(methodcaller(Path.with_suffix.__name__, ''),
                            sources_relative_paths))


stdlib_modules_names = (set(find_stdlib_modules_names())
                        - {'antigravity', 'this'})

if sys.platform == 'win32':
    stdlib_modules_names -= {'crypt', 'curses', 'pty', 'tty'}

stdlib_modules = list(map(importlib.import_module, stdlib_modules_names))
supported_modules = set(stdlib_modules)
unsupported_modules = set()

if platform.python_implementation() != 'PyPy':
    import _lsprof
    import _multibytecodec
    import _string
    import aifc
    import audioop
    import bdb
    import ctypes
    import faulthandler
    import mailbox
    import parser
    import turtle
    import unittest
    import xxsubtype

    # not supported by ``typeshed`` package
    unsupported_modules.update({_lsprof,
                                _multibytecodec,
                                _string,
                                aifc,
                                audioop,
                                bdb,
                                ctypes,
                                faulthandler,
                                mailbox,
                                parser,
                                turtle,
                                unittest,
                                xxsubtype})

supported_modules -= unsupported_modules

is_module_supported = supported_modules.__contains__

modules = (strategies.sampled_from(stdlib_modules)
           .filter(is_module_supported))


def flatten_module_or_class(object_: Union[ModuleType, type]
                            ) -> SearchStrategy:
    return strategies.sampled_from(list(vars(object_).values()))


def is_object_supported(object_: Any) -> bool:
    return (not isinstance(object_, ModuleType)
            or is_module_supported(object_))


objects = modules.flatmap(flatten_module_or_class)


def is_not_private(object_: Union[BuiltinFunctionType,
                                  MethodDescriptorType,
                                  type]) -> bool:
    return not object_.__name__.startswith('_')


unsupported_classes = set()

if platform.python_implementation() != 'PyPy':
    import _ast
    import _collections
    import _collections_abc
    import _hashlib
    import _io
    import _thread
    import itertools
    import _json
    import _ssl
    import _weakrefset
    import encodings
    import macpath
    import pdb
    import random
    import runpy
    import smtplib
    import socket
    import struct
    import tarfile
    import tkinter
    import types
    import warnings

    # not supported by ``typeshed`` package
    unsupported_classes.update({_ast.excepthandler,
                                _collections._deque_iterator,
                                _collections._deque_reverse_iterator,
                                _collections_abc.dict_items,
                                _collections_abc.dict_keys,
                                _collections_abc.mappingproxy,
                                _collections_abc.range_iterator,
                                _hashlib.HASH,
                                _io._BufferedIOBase,
                                _io._IOBase,
                                _io._RawIOBase,
                                _io._TextIOBase,
                                _json.make_encoder,
                                _json.make_scanner,
                                _ssl._SSLContext,
                                _thread.LockType,
                                _thread.RLock,
                                _thread._local,
                                _weakrefset.ref,
                                itertools._grouper,
                                itertools._tee,
                                itertools._tee_dataobject,
                                encodings.CodecRegistryError,
                                macpath.norm_error,
                                os.terminal_size,
                                os.times_result,
                                os.uname_result,
                                pdb._rstr,
                                pdb.Restart,
                                random._MethodType,
                                runpy._Error,
                                smtplib.SMTPNotSupportedError,
                                socket._GiveupOnSendfile,
                                struct.Struct,
                                tarfile.EmptyHeaderError,
                                tarfile.EOFHeaderError,
                                tarfile.InvalidHeaderError,
                                tarfile.TruncatedHeaderError,
                                tarfile.SubsequentHeaderError,
                                tkinter.TclError,
                                types.CodeType,
                                types.FrameType,
                                types.ModuleType,
                                warnings._OptionError})
    if sys.platform == 'win32':
        unsupported_classes.update({os.statvfs_result})
    else:
        import pwd
        import termios

        unsupported_classes.update({os.sched_param,
                                    os.waitid_result,
                                    pwd.struct_passwd,
                                    termios.error})

    if sys.version_info < (3, 7):
        import plistlib

        unsupported_classes.add(plistlib._InternalDict)


def is_class_supported(class_: type) -> bool:
    return class_ not in unsupported_classes


classes = (objects.filter(inspect.isclass)
           .filter(is_class_supported)
           .filter(is_not_private))
classes_objects = classes.flatmap(flatten_module_or_class)
methods = classes_objects.filter(inspect.isfunction)


def is_method_descriptor(object_: Any) -> bool:
    return isinstance(object_, MethodDescriptorType)


unsupported_methods_descriptors = set()

if platform.python_implementation() != 'PyPy':
    import collections
    import zipimport

    # not supported by ``typeshed`` package
    unsupported_methods_descriptors.update({_collections_abc.generator.close,
                                            _collections_abc.generator.send,
                                            _collections_abc.generator.throw,
                                            _collections_abc.coroutine.close,
                                            _collections_abc.coroutine.send,
                                            _collections_abc.coroutine.throw,
                                            _io.BufferedRWPair.peek,
                                            collections.OrderedDict.clear,
                                            collections.OrderedDict.pop,
                                            collections.OrderedDict.setdefault,
                                            collections.OrderedDict.update,
                                            dict.get,
                                            int.conjugate,
                                            float.conjugate,
                                            zipimport.zipimporter.find_loader})
    if sys.version_info >= (3, 6):
        unsupported_methods_descriptors.update(
                {_collections_abc.async_generator.aclose,
                 _collections_abc.async_generator.asend,
                 _collections_abc.async_generator.athrow})
        if sys.platform == 'linux':
            import socket

            unsupported_methods_descriptors.add(socket.socket.sendmsg_afalg)
    if sys.version_info >= (3, 7):
        import socket

        unsupported_methods_descriptors.update({bytes.isascii,
                                                bytearray.isascii,
                                                socket.socket.getblocking,
                                                str.isascii})
    if sys.platform == 'win32':
        import socket

        unsupported_methods_descriptors.add(socket.socket.share)


def is_method_descriptor_supported(method_descriptor: MethodDescriptorType
                                   ) -> bool:
    return method_descriptor not in unsupported_methods_descriptors


methods_descriptors = (classes_objects.filter(is_method_descriptor)
                       .filter(is_not_private)
                       .filter(is_method_descriptor_supported))


def is_wrapper_descriptor(object_: Any) -> bool:
    return isinstance(object_, WrapperDescriptorType)


unsupported_wrappers_descriptors = set()

if platform.python_implementation() != 'PyPy':
    import _collections_abc

    # not supported by ``typeshed`` package
    unsupported_wrappers_descriptors.update({
        _collections_abc.coroutine.__del__,
        _collections_abc.generator.__del__})


def is_wrapper_descriptor_supported(wrapper_descriptor: MethodDescriptorType
                                    ) -> bool:
    return wrapper_descriptor not in unsupported_wrappers_descriptors


wrappers_descriptors = (classes_objects.filter(is_wrapper_descriptor)
                        .filter(is_wrapper_descriptor_supported))
functions = objects.filter(inspect.isfunction)

unsupported_built_in_functions = set()

if platform.python_implementation() != 'PyPy':
    import _hashlib
    import _json
    import _thread
    import codecs
    import socket

    # not supported by ``typeshed`` package
    unsupported_built_in_functions.update({_hashlib.openssl_md5,
                                           _hashlib.openssl_sha1,
                                           _hashlib.openssl_sha224,
                                           _hashlib.openssl_sha256,
                                           _hashlib.openssl_sha384,
                                           _hashlib.openssl_sha512,
                                           _json.encode_basestring,
                                           _thread.allocate,
                                           _thread.exit_thread,
                                           _thread.interrupt_main,
                                           _thread.stack_size,
                                           _thread.start_new_thread,
                                           codecs.backslashreplace_errors,
                                           codecs.ignore_errors,
                                           codecs.namereplace_errors,
                                           codecs.replace_errors,
                                           codecs.strict_errors,
                                           codecs.xmlcharrefreplace_errors,
                                           os.get_inheritable,
                                           os.set_inheritable,
                                           socket.dup,
                                           sys.callstats,
                                           sys.getallocatedblocks,
                                           sys.get_coroutine_wrapper,
                                           sys.set_coroutine_wrapper})
    if sys.version_info >= (3, 6):
        unsupported_built_in_functions.update({sys.getfilesystemencodeerrors,
                                               sys.get_asyncgen_hooks,
                                               sys.set_asyncgen_hooks})
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
callables = (built_in_functions
             | classes
             | functions
             | methods
             | methods_descriptors
             | wrappers_descriptors)
