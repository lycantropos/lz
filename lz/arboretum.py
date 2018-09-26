import ast
import builtins
import collections
import importlib
from functools import singledispatch
from pathlib import Path
from typing import (Any,
                    Dict,
                    Iterable,
                    Union)

from lz import left
from . import (catalog,
               namespaces,
               sources)
from .hints import Namespace

Nodes = Dict[catalog.Path, ast.AST]

built_ins_namespace = namespaces.factory(builtins)


def module_path_to_nodes(module_path: catalog.Path) -> Nodes:
    result = {}
    source_path = sources.factory(module_path)
    module_root = factory(source_path)
    namespace = namespaces.factory(module_path)
    namespace = namespaces.merge([built_ins_namespace, namespace])
    NodeTransformer(nodes=result,
                    namespace=namespace,
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


@factory.register(ast.Module)
def from_root_node(node: ast.Module) -> ast.Module:
    return node


@factory.register(ast.AST)
def from_node(node: ast.AST) -> ast.Module:
    return ast.Module([node])


def search_by_path(namespace: Namespace, path: catalog.Path) -> Any:
    return left.folder(getattr, namespace[path.parts[0]])(path.parts[1:])


def namespace_contains(namespace: Namespace, path: catalog.Path) -> bool:
    try:
        search_by_path(namespace, path)
    except (KeyError, AttributeError):
        return False
    else:
        return True


class BaseNodeTransformer(ast.NodeTransformer):
    def __init__(self,
                 *,
                 nodes: Nodes,
                 namespace: Namespace,
                 parent_path: catalog.Path) -> None:
        self.nodes = nodes
        self.namespace = namespace
        self.parent_path = parent_path

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        path = self.parent_path.join(node.name)
        self.nodes[path] = node
        transformer = BaseNodeTransformer(nodes=self.nodes,
                                          namespace=self.namespace,
                                          parent_path=path)
        yield from map(transformer.visit, node.body)
        yield node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        path = self.parent_path.join(node.name)
        self.nodes[path] = node
        return node

    def visit_Import(self, node: ast.Import) -> Any:
        for child in node.names:
            alias_path = to_alias_path(child)
            actual_path = to_actual_path(child)
            if not namespace_contains(self.namespace, alias_path):
                parent_module_name = actual_path.parts[0]
                module = importlib.import_module(parent_module_name)
                self.namespace[parent_module_name] = module
            self.nodes[alias_path] = node
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        module_path = self.parent_path.join(catalog.factory(node.module))
        for child in node.names:
            alias_path = to_alias_path(child)
            actual_path = to_actual_path(child)
            if not namespace_contains(self.namespace, alias_path):
                namespace = namespaces.factory(module_path)
                self.namespace[str(alias_path)] = search_by_path(namespace,
                                                                 actual_path)
            self.nodes[alias_path] = node
        return node

    def visit_If(self, node: ast.If) -> Any:
        if self.visit(node.test):
            yield from map(self.visit, node.body)
        else:
            yield from map(self.visit, node.orelse)

    def visit_Assign(self, node: ast.Assign) -> Any:
        paths = map(self.visit, node.targets)
        value_node = node.value
        for path in paths:
            self.nodes[path] = value_node
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        self.nodes[self.visit(node.target)] = node.value
        return node

    def visit_Name(self, node: ast.Name) -> Any:
        return catalog.factory(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        return self.visit(node.value).join(node.attr)

    def visit_alias(self, alias: ast.alias) -> catalog.Path:
        result = alias.asname
        if result is None:
            result = alias.name
        return catalog.factory(result)

    def visit_Compare(self, node: ast.Compare) -> bool:
        nodes = {}
        transformer = BaseNodeTransformer(nodes=nodes,
                                          namespace=self.namespace,
                                          parent_path=self.parent_path)
        for child in ast.iter_child_nodes(node):
            transformer.visit(child)
        if nodes:
            for path, node in nodes.items():
                if str(path) in self.namespace:
                    continue
                evaluate(node,
                         namespace=self.namespace)
            self.nodes.update(nodes)
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


class NodeTransformer(BaseNodeTransformer):
    def __init__(self,
                 *,
                 nodes: Nodes,
                 namespace: Namespace,
                 parent_path: catalog.Path) -> None:
        super().__init__(nodes=nodes,
                         namespace=namespace,
                         parent_path=parent_path)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        module_path = catalog.factory(node.module)
        for child in node.names:
            alias_path = to_alias_path(child)
            actual_path = to_actual_path(child)
            actual_full_path = module_path.join(actual_path)
            try:
                source_path = sources.factory(actual_full_path)
            except ImportError:
                source_path = sources.factory(module_path)
                namespace = namespaces.factory(module_path)
            else:
                namespace = namespaces.factory(actual_full_path)
            if not namespace_contains(self.namespace, alias_path):
                self.namespace[str(alias_path)] = search_by_path(namespace,
                                                                 actual_path)
            nodes = {}
            module_tree = factory(source_path)
            BaseNodeTransformer(nodes=nodes,
                                namespace=namespace,
                                parent_path=catalog.Path()).visit(module_tree)
            target_node = nodes[actual_path]
            if isinstance(target_node, (ast.Import, ast.ImportFrom)):
                # handle chained imports
                nodes = {}
                NodeTransformer(nodes=nodes,
                                namespace=namespace,
                                parent_path=module_path).visit(target_node)
                target_node = nodes[actual_path]
            self.nodes[alias_path] = target_node
        return node


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
