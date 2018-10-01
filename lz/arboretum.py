import ast
import builtins
import importlib
from functools import singledispatch
from itertools import chain
from pathlib import Path
from typing import (Any,
                    Dict,
                    Iterable)

from . import (catalog,
               left,
               namespaces,
               sources)
from .hints import Namespace
from .iterating import expand

Nodes = Dict[catalog.Path, ast.AST]


def to_node(object_: Any) -> ast.AST:
    module_path = catalog.factory(catalog.module_name_factory(object_))
    nodes = module_path_to_nodes(module_path)
    object_path = catalog.factory(object_)
    Reducer(nodes=nodes,
            parent_path=catalog.Path()).visit(nodes[object_path])
    return nodes[object_path]


built_ins_namespace = namespaces.factory(builtins)


def module_path_to_nodes(module_path: catalog.Path) -> Nodes:
    result = {}
    source_path = sources.factory(module_path)
    module_root = factory(source_path)
    namespace = namespaces.factory(module_path)
    namespace = namespaces.merge([built_ins_namespace, namespace])
    Flattener(namespace=namespace,
              module_path=module_path,
              parent_path=catalog.Path()).visit(module_root)
    Registry(nodes=result,
             parent_path=catalog.Path()).visit(module_root)
    return result


@singledispatch
def factory(object_: Any) -> ast.Module:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


@factory.register(Path)
def from_source_path(path: Path) -> ast.Module:
    with open(path) as module_file:
        module_source = module_file.read()
    return ast.parse(module_source)


@factory.register(catalog.Path)
def from_module_path(path: catalog.Path) -> ast.Module:
    return factory(sources.factory(path))


@factory.register(ast.Module)
def from_root_node(node: ast.Module) -> ast.Module:
    return node


@factory.register(ast.AST)
def from_node(node: ast.AST) -> ast.Module:
    return ast.Module([node])


class Base(ast.NodeTransformer):
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

    def visit_Import(self, node: ast.Import) -> Iterable[ast.Import]:
        for name_alias in node.names:
            alias_path = self.resolve_path(to_alias_path(name_alias))
            actual_path = to_actual_path(name_alias)
            if not namespace_contains(self.namespace, alias_path):
                parent_module_name = actual_path.parts[0]
                module = importlib.import_module(parent_module_name)
                self.namespace[parent_module_name] = module
            yield ast.Import([name_alias])

    def visit_ImportFrom(self, node: ast.ImportFrom
                         ) -> Iterable[ast.ImportFrom]:
        parent_module_path = to_parent_module_path(
                node,
                parent_module_path=self.module_path)
        for name_alias in node.names:
            alias_path = self.resolve_path(to_alias_path(name_alias))
            actual_path = to_actual_path(name_alias)
            if not namespace_contains(self.namespace, alias_path):
                namespace = namespaces.factory(parent_module_path)
                self.namespace[str(alias_path)] = search_by_path(namespace,
                                                                 actual_path)
            yield ast.ImportFrom(str(parent_module_path), [name_alias], 0)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        path = self.resolve_path(catalog.factory(node.name))
        transformer = type(self)(namespace=self.namespace,
                                 parent_path=path,
                                 module_path=self.module_path,
                                 is_nested=True)
        for child in node.body:
            transformer.visit(child)
        return node

    def visit_If(self, node: ast.If) -> Iterable[ast.AST]:
        if self.visit(node.test):
            children = node.body
        else:
            children = node.orelse
        for child in children:
            self.visit(child)
        yield from children

    def visit_BoolOp(self, node: ast.BoolOp) -> bool:
        return self.evaluate_condition(node)

    def visit_Compare(self, node: ast.Compare) -> bool:
        return self.evaluate_condition(node)

    def evaluate_condition(self, node):
        nodes = {}
        transformer = type(self)(namespace=self.namespace,
                                 module_path=self.module_path,
                                 parent_path=self.parent_path)
        for child in ast.iter_child_nodes(node):
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

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        path = self.resolve_path(catalog.factory(node.name))
        self.nodes[path] = node
        transformer = type(self)(nodes=self.nodes,
                                 parent_path=path,
                                 is_nested=True)
        for child in node.body:
            transformer.visit(child)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        path = self.resolve_path(catalog.factory(node.name))
        self.nodes[path] = node
        return node

    def visit_Import(self, node: ast.Import) -> ast.Import:
        for child in node.names:
            alias_path = self.resolve_path(to_alias_path(child))
            self.nodes[alias_path] = node
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        for child in node.names:
            alias_path = self.resolve_path(to_alias_path(child))
            self.nodes[alias_path] = node
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        paths = map(self.visit, node.targets)
        value_node = node.value
        for path in paths:
            self.nodes[path] = value_node
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AnnAssign:
        path = self.visit(node.target)
        self.nodes[path] = node.value
        return node

    def visit_Name(self, node: ast.Name) -> catalog.Path:
        name_path = catalog.factory(node.id)
        if isinstance(node.ctx, ast.Load):
            return name_path
        elif isinstance(node.ctx, ast.Store):
            return self.resolve_path(name_path)

    def visit_Attribute(self, node: ast.Attribute) -> catalog.Path:
        parent_path = self.visit(node.value)
        attribute_path = catalog.factory(node.attr)
        return parent_path.join(attribute_path)

    def visit_Subscript(self, node: ast.Subscript) -> ast.Subscript:
        context = node.ctx
        if not isinstance(context, ast.Load):
            raise TypeError('Unsupported context type: {type}.'
                            .format(type=type(context)))
        return node


class Reducer(Base):
    def __init__(self,
                 *,
                 nodes: Nodes,
                 parent_path: catalog.Path,
                 is_nested: bool = False) -> None:
        super().__init__(parent_path=parent_path,
                         is_nested=is_nested)
        self.nodes = nodes

    def visit_Import(self, node: ast.Import) -> ast.Import:
        for child in node.names:
            alias_path = to_alias_path(child)
            actual_path = to_actual_path(child)
            nodes = module_path_to_nodes(actual_path)
            self.nodes.update(dict(zip(map(alias_path.join, nodes.keys()),
                                       nodes.values())))
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
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
                target_node = nodes[actual_path]
                if isinstance(target_node, (ast.Import, ast.ImportFrom)):
                    # handle chained imports
                    nodes = {}
                    submodule_path = parent_module_path.join(
                            catalog.factory(target_node.module))
                    type(self)(nodes=nodes,
                               namespace={},
                               parent_path=parent_module_path,
                               module_path=submodule_path).visit(target_node)
                    target_node = nodes[actual_path]
                self.nodes[alias_path] = target_node
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        path = self.resolve_path(catalog.factory(node.name))
        transformer = type(self)(nodes=self.nodes,
                                 parent_path=path,
                                 is_nested=True)
        for child in node.body:
            transformer.visit(child)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        parent_path = self.visit(node.value)
        attribute_path = catalog.factory(node.attr)
        object_path = parent_path.join(attribute_path)
        self.nodes[attribute_path] = self.nodes[object_path]
        return node

    def visit_Name(self, node: ast.Name) -> catalog.Path:
        path = catalog.factory(node.id)
        node = self.nodes[path]
        self.visit(node)
        return path


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


def to_parent_module_path(object_: ast.ImportFrom,
                          *,
                          parent_module_path: catalog.Path) -> catalog.Path:
    level = object_.level
    import_is_relative = level > 0
    if not import_is_relative:
        return catalog.factory(object_.module)
    module_path_parts = filter(None,
                               chain(parent_module_path.parts[:1 - level],
                                     expand(object_.module)))
    return catalog.Path(*module_path_parts)


def to_alias_path(node: ast.alias) -> catalog.Path:
    result = node.asname
    if result is None:
        result = node.name
    return catalog.factory(result)


def to_actual_path(node: ast.alias) -> catalog.Path:
    return catalog.factory(node.name)


def expression_to_assignment(node: ast.expr,
                             *,
                             name: str) -> ast.Assign:
    name_node = ast.Name(name, ast.Store())
    result = ast.Assign([name_node], node)
    result = ast.fix_missing_locations(result)
    return result


@singledispatch
def evaluate(node: ast.AST,
             *,
             namespace: Namespace) -> None:
    raise TypeError('Unsupported node type: {type}.'
                    .format(type=type(node)))


@evaluate.register(ast.stmt)
def evaluate_statement(node: ast.stmt,
                       *,
                       namespace: Namespace) -> None:
    evaluate_tree(factory(node),
                  namespace=namespace)


@evaluate.register(ast.Module)
def evaluate_tree(node: ast.Module,
                  *,
                  namespace: Namespace) -> None:
    code = compile(node, '<ast>', 'exec')
    exec(code, namespace)
