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
        paths = map(self.visit, node.names)
        for path in paths:
            if not namespace_contains(self.namespace, path):
                parent_module_name = path.parts[0]
                module = importlib.import_module(parent_module_name)
                self.namespace[parent_module_name] = module
            self.nodes[path] = node
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        paths = map(self.visit, node.names)
        for path in paths:
            self.nodes[path] = node
        module_path = catalog.factory(node.module)
        self.namespace.update(namespaces.factory(module_path))
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
        def to_nodes(node_or_list: Union[ast.AST, Iterable[ast.AST]]
                     ) -> Iterable[ast.AST]:
            if isinstance(node_or_list, collections.Iterable):
                yield from node_or_list
            else:
                yield node_or_list

        nodes = {}
        transformer = BaseNodeTransformer(nodes=nodes,
                                          namespace=self.namespace,
                                          parent_path=self.parent_path)
        for field_name in node._fields:
            children = to_nodes(getattr(node, field_name))
            for child in children:
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
        module_path = self.parent_path.join(catalog.factory(node.module))
        paths = map(self.visit, node.names)
        for path in paths:
            object_path = module_path.join(path)
            try:
                source_path = sources.factory(object_path)
            except ImportError:
                source_path = sources.factory(module_path)
                namespace = namespaces.factory(module_path)
            else:
                namespace = namespaces.factory(object_path)
            self.namespace.update(namespace)
            nodes = {}
            module_tree = factory(source_path)
            BaseNodeTransformer(nodes=nodes,
                                namespace=namespace,
                                parent_path=catalog.Path()).visit(module_tree)
            target_node = nodes[path]
            if isinstance(target_node, (ast.Import, ast.ImportFrom)):
                # handle chained imports
                nodes = {}
                NodeTransformer(nodes=nodes,
                                namespace=namespace,
                                parent_path=module_path).visit(target_node)
                target_node = nodes[path]
            self.nodes[path] = target_node
        return node


def expression_to_assignment(node: ast.expr,
                             *,
                             name: str) -> ast.Assign:
    name_node = ast.Name(name, ast.Store())
    result = ast.Assign([name_node], node)
    for attribute in result._attributes:
        setattr(result, attribute, getattr(node, attribute))
        setattr(name_node, attribute, getattr(node, attribute))
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
    code = compile(node, __file__, 'exec')
    exec(code, namespace)
