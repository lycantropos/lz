import importlib
import inspect
import os
import platform
import sys
from importlib.machinery import ModuleSpec
from operator import methodcaller
from pathlib import Path
from types import (BuiltinFunctionType,
                   ModuleType)
from typing import (Any,
                    Iterable,
                    List,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from lz.functional import compose
from lz.iterating import flatmapper
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

if platform.python_implementation() == 'PyPy':
    stdlib_modules_names -= {'msilib', 'symtable', 'tracemalloc'}

stdlib_modules = list(map(importlib.import_module, stdlib_modules_names))
supported_modules = set(stdlib_modules)
unsupported_modules = set()

if platform.python_implementation() != 'PyPy':
    import _collections
    import _codecs_hk
    import _codecs_iso2022
    import _codecs_jp
    import _codecs_kr
    import _codecs_cn
    import _codecs_tw
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
    unsupported_modules.update({_collections,
                                _codecs_hk,
                                _codecs_iso2022,
                                _codecs_jp,
                                _codecs_kr,
                                _codecs_cn,
                                _codecs_tw,
                                _lsprof,
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

    if sys.version_info >= (3, 6):
        import _sha3

        unsupported_modules.add(_sha3)

    if ((3, 6) <= sys.version_info < (3, 6, 7)
            or (3, 7) <= sys.version_info < (3, 7, 1)):
        import _blake2

        unsupported_modules.add(_blake2)

supported_modules -= unsupported_modules

is_module_supported = supported_modules.__contains__

modules = (strategies.sampled_from(stdlib_modules)
           .filter(is_module_supported))


def flatten_module_or_class(object_: Union[ModuleType, type]
                            ) -> SearchStrategy:
    return strategies.sampled_from(object_to_contents(object_))


def object_to_contents(object_: Union[ModuleType, type]) -> List[Any]:
    return list(vars(object_).values())


objects_to_contents = compose(list, flatmapper(object_to_contents))
unsupported_modules_objects = objects_to_contents(unsupported_modules)


def is_object_supported(object_: Any) -> bool:
    if isinstance(object_, ModuleSpec):
        return False
    return (object_ not in unsupported_modules_objects
            and (not isinstance(object_, ModuleType)
                 or is_module_supported(object_)))


objects = (modules.flatmap(flatten_module_or_class)
           .filter(is_object_supported))


def is_not_private(object_: Union[BuiltinFunctionType,
                                  MethodDescriptorType,
                                  type]) -> bool:
    return not object_.__name__.startswith('_')


unsupported_classes = set()

if platform.python_implementation() != 'PyPy':
    import _ast
    import _collections_abc
    import _io
    import _json
    import _ssl
    import _thread
    import _weakrefset
    import asyncio.events
    import encodings
    import itertools
    import macpath
    import pdb
    import random
    import runpy
    import smtplib
    import socket
    import tarfile
    import tkinter
    import types
    import warnings

    # not supported by ``typeshed`` package
    unsupported_classes.update({_ast.excepthandler,
                                _collections_abc.mappingproxy,
                                _io._BufferedIOBase,
                                _io._IOBase,
                                _io._RawIOBase,
                                _io._TextIOBase,
                                _ssl._SSLContext,
                                _thread.RLock,
                                _thread._local,
                                _weakrefset.ref,
                                asyncio.events._RunningLoop,
                                itertools._grouper,
                                itertools._tee,
                                itertools._tee_dataobject,
                                encodings.CodecRegistryError,
                                macpath.norm_error,
                                pdb._rstr,
                                pdb.Restart,
                                random._MethodType,
                                runpy._Error,
                                smtplib.SMTPNotSupportedError,
                                socket._GiveupOnSendfile,
                                tarfile.EmptyHeaderError,
                                tarfile.EOFHeaderError,
                                tarfile.InvalidHeaderError,
                                tarfile.TruncatedHeaderError,
                                tarfile.SubsequentHeaderError,
                                tkinter.TclError,
                                warnings._OptionError})

    if sys.version_info >= (3, 6):
        import asyncio.base_futures

        unsupported_classes.update({_ast.Constant,
                                    asyncio.base_futures.InvalidStateError})

    if sys.version_info < (3, 7):
        import os
        import plistlib

        unsupported_classes.update({_collections_abc.range_iterator,
                                    os.terminal_size,
                                    os.times_result,
                                    os.uname_result,
                                    plistlib._InternalDict})
    else:
        import dataclasses
        import typing

        unsupported_classes.update({asyncio.events.SendfileNotAvailableError,
                                    dataclasses._InitVarMeta,
                                    typing._ProtocolMeta})

    if sys.platform == 'win32':
        import subprocess

        unsupported_classes.add(subprocess.Handle)
    else:
        import pwd
        import termios

        unsupported_classes.update({os.waitid_result,
                                    pwd.struct_passwd,
                                    termios.error})


def is_class_supported(class_: type) -> bool:
    return class_ not in unsupported_classes


classes = (objects.filter(inspect.isclass)
           .filter(is_class_supported)
           .filter(is_not_private))
classes_objects = (classes.flatmap(flatten_module_or_class)
                   .filter(is_object_supported))
methods = classes_objects.filter(inspect.isfunction)


def is_method_descriptor(object_: Any) -> bool:
    return isinstance(object_, MethodDescriptorType)


unsupported_methods_descriptors = set()

if platform.python_implementation() != 'PyPy':
    import _collections_abc
    import _io
    import _thread
    import collections
    import types

    # not supported by ``typeshed`` package
    unsupported_methods_descriptors.update(
            {_collections_abc.dict_items.isdisjoint,
             _collections_abc.generator.close,
             _collections_abc.generator.send,
             _collections_abc.generator.throw,
             _collections_abc.coroutine.close,
             _collections_abc.coroutine.send,
             _collections_abc.coroutine.throw,
             _io.BufferedRWPair.peek,
             _thread.LockType.acquire,
             _thread.LockType.acquire_lock,
             _thread.LockType.locked,
             _thread.LockType.locked_lock,
             _thread.LockType.release,
             _thread.LockType.release_lock,
             collections.OrderedDict.clear,
             collections.OrderedDict.pop,
             collections.OrderedDict.update,
             int.conjugate,
             types.FrameType.clear})

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
                                                socket.socket.getblocking})
    else:
        import zipimport

        unsupported_methods_descriptors.update(
                {collections.OrderedDict.setdefault,
                 dict.get,
                 float.conjugate,
                 zipimport.zipimporter.find_loader})

    if sys.platform == 'win32':
        import socket

        unsupported_methods_descriptors.add(socket.socket.share)


def is_method_descriptor_supported(method_descriptor: MethodDescriptorType
                                   ) -> bool:
    return (is_not_private(method_descriptor)
            and method_descriptor not in unsupported_methods_descriptors)


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
                                           socket.dup,
                                           sys.callstats,
                                           sys.getallocatedblocks,
                                           sys.get_coroutine_wrapper,
                                           sys.set_coroutine_wrapper})
    if sys.version_info >= (3, 6):
        unsupported_built_in_functions.update({sys.getfilesystemencodeerrors,
                                               sys.get_asyncgen_hooks,
                                               sys.set_asyncgen_hooks})

    if sys.version_info >= (3, 7):
        unsupported_built_in_functions.update({socket.close,
                                               sys.breakpointhook})

    if sys.platform != 'win32':
        import _locale

        unsupported_built_in_functions.update(
                {_locale.bind_textdomain_codeset,
                 _locale.bindtextdomain,
                 _locale.dcgettext,
                 _locale.dgettext,
                 _locale.gettext,
                 _locale.textdomain})

        if sys.version_info >= (3, 7):
            import time

            unsupported_built_in_functions.add(time.pthread_getcpuclockid)


def is_built_in_function_supported(function: BuiltinFunctionType) -> bool:
    return (is_not_private(function)
            and has_module(function)
            and function not in unsupported_built_in_functions)


def has_module(function: BuiltinFunctionType) -> bool:
    return bool(function.__module__)


built_in_functions = (objects.filter(inspect.isbuiltin)
                      .filter(is_built_in_function_supported))
unsupported_callables = strategies.sampled_from(
        list(unsupported_built_in_functions
             | unsupported_classes
             | unsupported_methods_descriptors
             | unsupported_wrappers_descriptors))
callables = (built_in_functions
             | classes
             | functions
             | methods
             | methods_descriptors
             | wrappers_descriptors)
