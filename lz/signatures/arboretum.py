import builtins
import importlib
from functools import singledispatch
from itertools import chain
from pathlib import Path
from typing import (Any,
                    Dict,
                    Iterable,
                    List)

from typed_ast import ast3

from lz import (left,
                right)
from lz.iterating import expand
from . import (catalog,
               dictionaries,
               namespaces,
               sources)
from .conversion import TypedToPlain
from .hints import Namespace

Nodes = Dict[catalog.Path, ast3.AST]

TYPING_MODULE_PATH = catalog.factory('typing')
OVERLOAD_DECORATORS_PATHS = {catalog.factory('typing.overload'),
                             catalog.factory('overload')}


def to_nodes(object_path: catalog.Path,
             module_path: catalog.Path) -> List[ast3.AST]:
    nodes = module_path_to_nodes(module_path)
    nodes = dictionaries.merge([built_ins_nodes, nodes])
    reducer = Reducer(nodes=nodes, parent_path=catalog.Path())
    reducer.visit(nodes[catalog.Path()])
    try:
        result = nodes[object_path]
    except KeyError:
        reducer.visit(nodes[object_path.parent])
        result = nodes[object_path]
    if not isinstance(result, list):
        result = [result]
    return result


def module_path_to_nodes(module_path: catalog.Path) -> Nodes:
    result = {}
    source_path = sources.factory(module_path)
    module_root = factory(source_path)
    namespace = namespaces.factory(module_path)
    namespace = dictionaries.merge([built_ins_namespace, namespace])
    Flattener(namespace=namespace,
              module_path=module_path,
              parent_path=catalog.Path()).visit(module_root)
    Registry(nodes=result,
             parent_path=catalog.Path()).visit(module_root)
    return result


@singledispatch
def factory(object_: Any) -> ast3.Module:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


@factory.register(Path)
def from_source_path(path: Path) -> ast3.Module:
    return ast3.parse(path.read_text())


@factory.register(catalog.Path)
def from_module_path(path: catalog.Path) -> ast3.Module:
    return factory(sources.factory(path))


@factory.register(ast3.Module)
def from_root_node(node: ast3.Module) -> ast3.Module:
    return node


@factory.register(ast3.AST)
def from_node(node: ast3.AST) -> ast3.Module:
    return ast3.Module([node], [])


class Base(ast3.NodeTransformer):
    def __init__(self,
                 *,
                 parent_path: catalog.Path,
                 is_nested: bool = False) -> None:
        self.parent_path = parent_path
        self.is_nested = is_nested

    def resolve_path(self, path: catalog.Path) -> catalog.Path:
        if self.is_nested:
            return self.parent_path.join(path)
        return path


class Flattener(Base):
    def __init__(self,
                 *,
                 namespace: Namespace,
                 module_path: catalog.Path,
                 parent_path: catalog.Path,
                 is_nested: bool = False) -> None:
        super().__init__(parent_path=parent_path,
                         is_nested=is_nested)
        self.namespace = namespace
        self.module_path = module_path

    def visit_Import(self, node: ast3.Import) -> Iterable[ast3.Import]:
        for name_alias in node.names:
            alias_path = self.resolve_path(to_alias_path(name_alias))
            actual_path = to_actual_path(name_alias)
            if not namespace_contains(self.namespace, alias_path):
                parent_module_name = actual_path.parts[0]
                module = importlib.import_module(parent_module_name)
                self.namespace[parent_module_name] = module
            yield ast3.Import([name_alias])

    def visit_ImportFrom(self, node: ast3.ImportFrom
                         ) -> Iterable[ast3.ImportFrom]:
        parent_module_path = to_parent_module_path(
                node,
                parent_module_path=self.module_path)
        for name_alias in node.names:
            alias_path = self.resolve_path(to_alias_path(name_alias))
            actual_path = to_actual_path(name_alias)
            if actual_path == catalog.WILDCARD_IMPORT:
                self.namespace.update(namespaces.factory(parent_module_path))
                yield from module_path_to_nodes(parent_module_path).values()
                continue
            elif not namespace_contains(self.namespace, alias_path):
                namespace = namespaces.factory(parent_module_path)
                try:
                    self.namespace[str(alias_path)] = search_by_path(
                            namespace,
                            actual_path)
                except KeyError:
                    module_path = parent_module_path.join(actual_path)
                    self.namespace[str(alias_path)] = importlib.import_module(
                            str(module_path))
            yield ast3.ImportFrom(str(parent_module_path), [name_alias], 0)

    def visit_ClassDef(self, node: ast3.ClassDef) -> ast3.ClassDef:
        path = self.resolve_path(catalog.factory(node.name))
        transformer = type(self)(namespace=self.namespace,
                                 parent_path=path,
                                 module_path=self.module_path,
                                 is_nested=True)
        for child in node.body:
            transformer.visit(child)
        return node

    def visit_If(self, node: ast3.If) -> Iterable[ast3.AST]:
        if self.visit(node.test):
            children = node.body
        else:
            children = node.orelse
        for child in children:
            self.visit(child)
        yield from children

    def visit_BoolOp(self, node: ast3.BoolOp) -> bool:
        return self.evaluate_expression(node)

    def visit_Compare(self, node: ast3.Compare) -> bool:
        return self.evaluate_expression(node)

    def evaluate_expression(self, node: ast3.expr) -> Any:
        nodes = {}
        transformer = type(self)(namespace=self.namespace,
                                 module_path=self.module_path,
                                 parent_path=self.parent_path)
        for child in ast3.iter_child_nodes(node):
            transformer.visit(child)
        if nodes:
            for path, node in nodes.items():
                if namespace_contains(self.namespace, path):
                    continue
                evaluate(node,
                         namespace=self.namespace)
        # to avoid name conflicts
        # we're using name that won't be present
        # because it'll lead to ``SyntaxError`` otherwise
        # and no AST will be generated
        temporary_name = '@tmp'
        assignment = expression_to_assignment(node,
                                              name=temporary_name)
        evaluate(assignment,
                 namespace=self.namespace)
        return self.namespace.pop(temporary_name)


class Registry(Base):
    def __init__(self,
                 *,
                 nodes: Nodes,
                 parent_path: catalog.Path,
                 is_nested: bool = False) -> None:
        super().__init__(parent_path=parent_path,
                         is_nested=is_nested)
        self.nodes = nodes

    def visit_Module(self, node: ast3.Module) -> ast3.Module:
        self.nodes[catalog.Path()] = node
        for child in node.body:
            self.visit(child)
        return node

    def visit_ClassDef(self, node: ast3.ClassDef) -> ast3.ClassDef:
        path = self.resolve_path(catalog.factory(node.name))
        self.nodes[path] = node
        transformer = type(self)(nodes=self.nodes,
                                 parent_path=path,
                                 is_nested=True)
        for child in node.body:
            transformer.visit(child)
        return node

    def visit_FunctionDef(self, node: ast3.FunctionDef) -> ast3.FunctionDef:
        path = self.resolve_path(catalog.factory(node.name))
        if self.is_overloaded(node):
            self.nodes.setdefault(path, []).append(node)
        else:
            self.nodes[path] = node
        return node

    def is_overloaded(self, node: ast3.FunctionDef) -> bool:
        decorators_paths = map(self.visit, node.decorator_list)
        overload_decorators_paths = (OVERLOAD_DECORATORS_PATHS
                                     & set(decorators_paths))
        try:
            overload_decorator_path, = overload_decorators_paths
        except ValueError:
            pass
        else:
            root_path = catalog.factory(overload_decorator_path.parts[0])
            root_node = self.nodes[root_path]
            if isinstance(root_node, ast3.Import):
                imported_modules_paths = map(to_actual_path, root_node.names)
                if any(module_path == TYPING_MODULE_PATH
                       for module_path in imported_modules_paths):
                    return True
            elif isinstance(root_node, ast3.ImportFrom):
                imported_from_module_path = catalog.factory(root_node.module)
                if imported_from_module_path == TYPING_MODULE_PATH:
                    return True
        return False

    def visit_Import(self, node: ast3.Import) -> ast3.Import:
        for child in node.names:
            alias_path = self.resolve_path(to_alias_path(child))
            self.nodes[alias_path] = node
        return node

    def visit_ImportFrom(self, node: ast3.ImportFrom) -> ast3.ImportFrom:
        for child in node.names:
            alias_path = self.resolve_path(to_alias_path(child))
            self.nodes[alias_path] = node
        return node

    def visit_Assign(self, node: ast3.Assign) -> ast3.Assign:
        paths = map(self.visit, node.targets)
        value_node = node.value
        for path in paths:
            self.nodes[path] = value_node
        return node

    def visit_AnnAssign(self, node: ast3.AnnAssign) -> ast3.AnnAssign:
        path = self.visit(node.target)
        self.nodes[path] = node
        return node

    def visit_Name(self, node: ast3.Name) -> catalog.Path:
        name_path = catalog.factory(node.id)
        if isinstance(node.ctx, ast3.Load):
            return name_path
        elif isinstance(node.ctx, ast3.Store):
            return self.resolve_path(name_path)

    def visit_Attribute(self, node: ast3.Attribute) -> catalog.Path:
        parent_path = self.visit(node.value)
        attribute_path = catalog.factory(node.attr)
        return parent_path.join(attribute_path)


complete_new_style_class_bases = right.attacher(ast3.Name('object',
                                                          ast3.Load()))


class Reducer(Base):
    def __init__(self,
                 *,
                 nodes: Nodes,
                 parent_path: catalog.Path,
                 is_nested: bool = False) -> None:
        super().__init__(parent_path=parent_path,
                         is_nested=is_nested)
        self.nodes = nodes

    def visit_Import(self, node: ast3.Import) -> ast3.Import:
        for child in node.names:
            alias_path = to_alias_path(child)
            actual_path = to_actual_path(child)
            nodes = module_path_to_nodes(actual_path)
            self.nodes.update(dict(zip(map(alias_path.join, nodes.keys()),
                                       nodes.values())))
        return node

    def visit_ImportFrom(self, node: ast3.ImportFrom) -> ast3.ImportFrom:
        parent_module_path = catalog.factory(node.module)
        for name_alias in node.names:
            alias_path = self.resolve_path(to_alias_path(name_alias))
            actual_path = to_actual_path(name_alias)
            if actual_path == catalog.WILDCARD_IMPORT:
                nodes = module_path_to_nodes(parent_module_path)
                self.nodes.update(nodes)
                continue
            object_path = parent_module_path.join(actual_path)
            if is_module_path(object_path):
                module_root = factory(object_path)
                self.nodes[alias_path] = module_root
            else:
                nodes = module_path_to_nodes(parent_module_path)
                target_node = nodes.pop(actual_path)
                if isinstance(target_node, (ast3.Import, ast3.ImportFrom)):
                    # handle chained imports
                    nodes = {}
                    transformer = type(self)(nodes=nodes,
                                             parent_path=parent_module_path)
                    transformer.visit(target_node)
                    target_node = nodes.pop(actual_path)
                self.nodes[alias_path] = target_node
                # hack to be able to visit "imported" nodes
                self.nodes.update(nodes)
        return node

    def visit_ClassDef(self, node: ast3.ClassDef) -> ast3.ClassDef:
        path = self.resolve_path(catalog.factory(node.name))
        bases = complete_new_style_class_bases(node.bases)
        for base_path in map(self.visit, bases):
            base_nodes = {object_path: node
                          for object_path, node in self.nodes.items()
                          if object_path.is_child_of(base_path)
                          and object_path != base_path}
            for base_object_path, base_object_node in base_nodes.items():
                self.nodes.setdefault(base_object_path.with_parent(path),
                                      base_object_node)
        transformer = type(self)(nodes=self.nodes,
                                 parent_path=path,
                                 is_nested=True)
        for child in node.body:
            transformer.visit(child)
        return node

    def visit_FunctionDef(self, node: ast3.FunctionDef) -> ast3.FunctionDef:
        return node

    def visit_Assign(self, node: ast3.Assign) -> ast3.Assign:
        return node

    def visit_AnnAssign(self, node: ast3.AnnAssign) -> ast3.AnnAssign:
        return node

    def visit_Call(self, node: ast3.Call) -> catalog.Path:
        return self.visit(node.func)

    def visit_Attribute(self, node: ast3.Attribute) -> catalog.Path:
        parent_path = self.visit(node.value)
        attribute_path = catalog.factory(node.attr)
        object_path = parent_path.join(attribute_path)
        self.nodes[attribute_path] = self.nodes[object_path]
        return object_path

    def visit_Name(self, node: ast3.Name) -> catalog.Path:
        return self.resolve_path(catalog.factory(node.id))

    def visit_Subscript(self, node: ast3.Subscript) -> catalog.Path:
        context = node.ctx
        if not isinstance(context, ast3.Load):
            raise TypeError('Unsupported context type: {type}.'
                            .format(type=type(context)))
        return self.visit(node.value)


def search_by_path(namespace: Namespace, path: catalog.Path) -> Any:
    return left.folder(getattr, namespace[path.parts[0]])(path.parts[1:])


def namespace_contains(namespace: Namespace, path: catalog.Path) -> bool:
    try:
        search_by_path(namespace, path)
    except (KeyError, AttributeError):
        return False
    else:
        return True


def is_module_path(object_path: catalog.Path) -> bool:
    try:
        importlib.import_module(str(object_path))
    except ImportError:
        return False
    else:
        return True


def to_parent_module_path(object_: ast3.ImportFrom,
                          *,
                          parent_module_path: catalog.Path) -> catalog.Path:
    level = object_.level
    import_is_relative = level > 0
    if not import_is_relative:
        return catalog.factory(object_.module)
    depth = (len(parent_module_path.parts)
             + is_package(parent_module_path)
             - level) or None
    module_path_parts = filter(None,
                               chain(parent_module_path.parts[:depth],
                                     expand(object_.module)))
    return catalog.Path(*module_path_parts)


def is_package(module_path: catalog.Path) -> bool:
    return hasattr(importlib.import_module(str(module_path)), '__path__')


def to_alias_path(node: ast3.alias) -> catalog.Path:
    result = node.asname
    if result is None:
        result = node.name
    return catalog.factory(result)


def to_actual_path(node: ast3.alias) -> catalog.Path:
    return catalog.factory(node.name)


def expression_to_assignment(node: ast3.expr,
                             *,
                             name: str) -> ast3.Assign:
    name_node = ast3.Name(name, ast3.Store())
    result = ast3.Assign([name_node], node, None)
    result = ast3.fix_missing_locations(result)
    return result


@singledispatch
def evaluate(node: ast3.AST,
             *,
             namespace: Namespace) -> None:
    raise TypeError('Unsupported node type: {type}.'
                    .format(type=type(node)))


@evaluate.register(ast3.stmt)
def evaluate_statement(node: ast3.stmt,
                       *,
                       namespace: Namespace) -> None:
    evaluate_tree(factory(node),
                  namespace=namespace)


@evaluate.register(ast3.Module)
def evaluate_tree(node: ast3.Module,
                  *,
                  namespace: Namespace) -> None:
    node = TypedToPlain().visit(node)
    code = compile(node, '<unknown>', 'exec')
    exec(code, namespace)


built_ins_namespace = namespaces.factory(builtins)
built_ins_nodes = module_path_to_nodes(catalog.factory(builtins))
