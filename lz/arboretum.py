import ast
import builtins
import collections
from functools import singledispatch
from pathlib import Path
from typing import (Any,
                    Dict,
                    Iterable,
                    Union)

from . import (catalog,
               dictionaries,
               left,
               sources)

Nodes = Dict[catalog.Path, ast.AST]
Namespace = Dict[str, Any]

built_ins_paths = catalog.paths_factory(builtins,
                                        parent_path=catalog.Path())


def module_path_to_nodes(module_path: catalog.Path) -> Nodes:
    result = {}
    source_path = sources.factory(module_path)
    module_root = factory(source_path)
    paths = catalog.paths_factory(module_path,
                                  parent_path=catalog.Path())
    paths = dictionaries.merge([built_ins_paths, paths])
    NodeTransformer(result,
                    paths,
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


class NodeTransformer(ast.NodeTransformer):
    def __init__(self,
                 nodes: Nodes,
                 paths: catalog.Paths,
                 *,
                 parent_path: catalog.Path) -> None:
        self.nodes = nodes
        self.paths = paths
        self.parent_path = parent_path

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        path = self.parent_path.join(node.name)
        self.nodes[path] = node
        transformer = NodeTransformer(self.nodes,
                                      self.paths,
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
            self.nodes[path] = node
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        paths = map(self.visit, node.names)
        for path in paths:
            self.nodes[path] = node
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

    def visit_Name(self, node: ast.Name) -> Any:
        return catalog.factory(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        context = node.ctx
        if isinstance(context, ast.Load):
            parent_path = self.visit(node.value)
            return self.paths[parent_path.join(node.attr)]
        elif isinstance(context, ast.Store):
            parent_path = self.visit(node.value)
            return parent_path.join(node.attr)
        else:
            raise TypeError('Unsupported context type: {type}.'
                            .format(type=type(context)))

    def visit_alias(self, alias: ast.alias) -> catalog.Path:
        result = alias.asname
        if result is None:
            result = alias.name
        return catalog.factory(result)

    def visit_Compare(self, node: ast.Compare) -> bool:
        nodes = {}

        def to_nodes(node_or_list: Union[ast.AST, Iterable[ast.AST]]
                     ) -> Iterable[ast.AST]:
            if isinstance(node_or_list, collections.Iterable):
                yield from node_or_list
            else:
                yield node_or_list

        for field_name in node._fields:
            children = to_nodes(getattr(node, field_name))
            for child in children:
                NodeTransformer(nodes,
                                self.paths,
                                parent_path=self.parent_path).visit(child)
        if nodes:
            for path, node in nodes.items():
                if path in self.paths:
                    continue
                namespace = paths_to_namespace(self.paths)
                evaluate(node,
                         namespace=namespace)
                search_namespace = left.folder(getattr,
                                               namespace[path.parts[0]])
                self.paths[path] = search_namespace(path.parts[1:])
        namespace = paths_to_namespace(self.paths)
        # to avoid name conflicts
        # we're using name that won't be present
        # because it'll lead to ``SyntaxError`` otherwise
        # and no AST will be generated
        temporary_name = '@tmp'
        assignment = expression_to_assignment(node,
                                              name=temporary_name)
        evaluate(assignment,
                 namespace=namespace)
        return namespace.pop(temporary_name)


def paths_to_namespace(paths: catalog.Paths) -> Namespace:
    return {str(path): content
            for path, content in paths.items()
            if len(path.parts) == 1}


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
