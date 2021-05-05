#!/usr/bin/env python3

import json
import genericAST

return_stack = []

class Node:
    """
    Abstract base class for AST nodes

    __init__: Initialize attributes / children

    children: Method to return list of children.
    lineno: Line number in source file
    """

    lineno: int

    def children(self):
        """
        A sequence of all children that are Nodes
        """
        pass

    def to_generic_node(self) -> genericAST.GenericNode:

        raise NotImplementedError(
            f"to_generic_node not implemented for python node type {self.__class__.__name__}")

    # Set of attributes for a given node
    attr_names = ()


class FuncDecl(Node):
    def __init__(self, name, params, ret_type, body, lineno):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.lineno = lineno
        self.ret_stms = return_stack[:]
        return_stack.clear()

    def children(self):
        nodelist = [
            ('params', self.params),
            ('ret_type', self.ret_type),
            ('body', self.body)
        ]
        return tuple(nodelist)

    def to_generic_node(self) -> genericAST.FunctionDeclaration:
        return default_conversion(self, genericAST.FunctionDeclaration)
    attr_names = ('name', )


class FuncCall(Node):
    def __init__(self, name, params, lineno):
        self.name = name
        self.params = params
        self.lineno = lineno

    def children(self):
        nodelist = []
        if self.params is not None:
            nodelist.append(('params', self.params))
        return tuple(nodelist)

    def to_generic_node(self) -> genericAST.FunctionCall:
        return default_conversion(self, genericAST.FunctionCall)
    attr_names = ('name', )


class ParamList(Node):
    def __init__(self, params, lineno):
        self.lineno = lineno
        self.params = params

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(('params[%d]' % i, child))
        return nodelist

    def to_generic_node(self) -> genericAST.ParameterList:
        return default_conversion(self, genericAST.ParameterList)
    attr_names = ()


class Param(Node):
    def __init__(self, name, param_type, lineno):
        self.name = name
        self.param_type = param_type
        self.lineno = lineno

    def children(self):
        return (('param_type', self.param_type),)
    attr_names = ('name', )

    def to_generic_node(self) -> genericAST.Parameter:
        return default_conversion(self, genericAST.Parameter)


class StmList(Node):
    def __init__(self, stmt_lst, lineno):
        self.stmt_lst = stmt_lst
        self.lineno = lineno

    def children(self):
        nodelist = []
        for i, stmt in enumerate(self.stmt_lst or []):
            nodelist.append(('stmt[%d]' % i, stmt))
        return nodelist

    def to_generic_node(self) -> genericAST.StmList:
        return default_conversion(self, genericAST.StmList)
    attr_names = ()


class DeclStm(Node):
    def __init__(self, name, var_type, lineno):
        self.name = name
        self.var_type = var_type
        self.lineno = lineno

    def children(self):
        return (('type', self.var_type),)

    def to_generic_node(self) -> genericAST.VariableDeclaration:
        return default_conversion(self, genericAST.VariableDeclaration)


attr_names = ('name', )


class AssignStm(Node):
    def __init__(self, name, expr, lineno):
        self.name = name
        self.expr = expr
        self.lineno = lineno

    def children(self):
        return (('expr', self.expr),)

    def to_generic_node(self) -> genericAST.AssignStm:
        return default_conversion(self, genericAST.AssignStm)


attr_names = ('name', )


class IfStm(Node):
    def __init__(self, cond, body, else_branch, lineno):
        self.cond = cond
        self.body = body
        self.else_branch = else_branch
        self.lineno = lineno

    def children(self):
        nodelist = [
            ('cond', self.cond),
            ('body', self.body)
        ]
        if self.else_branch is not None:
            nodelist.append(('else', self.else_branch))
        return tuple(nodelist)
    attr_names = ()

    def to_generic_node(self) -> genericAST.IfStm:
        return default_conversion(self, genericAST.IfStm)


class ElifBlock(IfStm):
    pass


class ElseBlock(Node):
    def __init__(self, body, lineno):
        self.body = body
        self.lineno = lineno

    def children(self):
        return (('body', self.body),)

    def to_generic_node(self) -> genericAST.ElseBlock:
        return default_conversion(self, genericAST.ElseBlock)
    attr_names = ()


class WhileStm(Node):
    def __init__(self, cond, body, lineno):
        self.cond = cond
        self.body = body
        self.lineno = lineno

    def children(self):
        nodelist = []
        if self.cond is not None:
            nodelist.append(('cond', self.cond))
        if self.body is not None:
            nodelist.append(('body', self.body))
        return tuple(nodelist)

    def to_generic_node(self) -> genericAST.WhileStm:
        return default_conversion(self, genericAST.WhileStm)

    attr_names = ()


class RetStm(Node):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno
        return_stack.append(self)

    def children(self):
        return (('expr', self.expr),)

    def to_generic_node(self) -> genericAST.RetStm:
        return default_conversion(self, genericAST.RetStm)
    attr_names = ()


class Constant(Node):
    def __init__(self, const_type, value, lineno=0):
        self.const_type = const_type
        self.value = value
        self.lineno = lineno

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def to_generic_node(self) -> genericAST.Constant:
        return default_conversion(self, genericAST.Constant)

    attr_names = ('type', 'value', )


class BinOp(Node):
    def __init__(self, op, left, right, lineno):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno
        self.inferred_type = None

    def children(self):
        nodelist = []
        if self.left is not None:
            nodelist.append(('left', self.left))
        if self.right is not None:
            nodelist.append(('right', self.right))
        return tuple(nodelist)

    def to_generic_node(self) -> genericAST.BinaryOperation:
        return default_conversion(self, genericAST.BinaryOperation)
    attr_names = ('op', )


class UnaryOp(Node):
    def __init__(self, op, expr, lineno):
        self.op = op
        self.expr = expr
        self.lineno = lineno

    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(('expr', self.expr))
        return tuple(nodelist)

    def to_generic_node(self) -> genericAST.UnaryOperation:
        return default_conversion(self, genericAST.UnaryOperation)
    attr_names = ('op', )


class ExprList(Node):
    def __init__(self, exprs, lineno):
        self.exprs = exprs
        self.lineno = lineno

    def children(self):
        nodelist = []
        if self.exprs is not None:
            nodelist.extend(("expr[%d]" % i, expr)
                            for i, expr in enumerate(self.exprs))
        return nodelist

    def to_generic_node(self) -> genericAST.ExpressionList:
        return default_conversion(self, genericAST.ExpressionList)
    attr_names = ()


class List(Node):
    def __init__(self, expr_list, lineno):
        self.expr_list = expr_list
        self.lineno = lineno

    def children(self):
        nodelist = (("expr_list", self.expr_list),)
        return nodelist

    def to_generic_node(self) -> genericAST.List:
        return default_conversion(self, genericAST.List)
    attr_names = ()

class Index(Node):
    def __init__(self, etype, expr, expr_pos, lineno):
        self.etype = etype
        self.expr = expr
        self.expr_pos = expr_pos
        self.lineno = lineno
    
    def children(self):
        nodelist = [
            ('type', self.etype),
            ('expr', self.expr),
            ('expr_pos', self.expr_pos)
        ]
        return nodelist

    def to_generic_node(self) -> genericAST.Index:
        return default_conversion(self, genericAST.Index)
    attr_names = ()

class Slice(Node):
    def __init__(self, start, step, expr, end, lineno):
        self.start = start
        self.step = step
        self.expr = expr
        self.end = end
        if start is None:
            self.start = Constant(Type('int'), 0)
        if step is None:
            self.step = Constant(Type('int'), 1)
        if end is None:
            self.end = Constant(Type('int'), 2147483647)
        self.lineno = lineno

    def children(self):
        nodelist = [('expr', self.expr)]
        if self.start is not None:
            nodelist.append(('start', self.start))
        if self.step is not None:
            nodelist.append(('step', self.step))
        if self.end is not None:
            nodelist.append(('end', self.end))
        return nodelist

    def to_generic_node(self) -> genericAST.Slice:
        return default_conversion(self, genericAST.Slice)
    attr_names = ()

class Type(Node):
    def __init__(self, name, lineno=0):
        self.name = name
        self.lineno = lineno

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def to_generic_node(self) -> genericAST.Type:
        return default_conversion(self, genericAST.Type)
    attr_names = ('name', )


class NodeVisitor(object):
    """
    A base NodeVisitor class for visiting MiniJava nodes.
    Define your own visit_X methods to, where X is the class
    name you want to visit with these methods.

    Refer to visit_Program, for example
    """

    def visit(self, node, offset=0):
        """
        Your compiler can call this method to traverse through your AST
        """
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node, offset)

    def generic_visit(self, node, offset=0):
        """
        Default visit method that simply prints out given node's attributes,
        then traverses through its children. This is called if no explicit
        visitor function exists for a node.

        NOTE: A method within Node object with similar behaviour might be
              useful when debugging your project
        """
        lead = ' ' * offset

        output = f"{lead}{node.lineno} {node.__class__.__name__}: "

        if node.attr_names:
            vlist = [(n, getattr(node, n)) for n in node.attr_names]
            output += ', '.join('%s = %s' % v for v in vlist)

        print(output)

        for (_, child) in node.children():
            self.visit(child, offset=offset + 2)

    def toJSON(self, node):
        return json.dumps(self._toJSON(node), indent=4)

    def _toJSON(self, node):
        output = {}
        output['node_class'] = node.__class__.__name__
        output['lineno'] = node.lineno

        if node.attr_names:
            output['attributes'] = {}
            for n in node.attr_names:
                output['attributes'][n] = getattr(node, n)

        children = node.children()
        if children and len(children) > 0:
            output['children'] = {}
            for (child_name, child) in node.children():
                output['children'][child_name] = self._toJSON(child)

        return output


def default_conversion(node: Node, genericNodeClass) -> genericAST.GenericNode:
    kwargs = node.__dict__
    for k, v in kwargs.items():
        if isinstance(v, Node):
            kwargs[k] = v.to_generic_node()
        elif isinstance(v, list):
            kwargs[k] = [el.to_generic_node() for el in v]

    return genericNodeClass(**kwargs)


def python_ast_to_generic(root):
    generic_root = genericAST.Program(lineno=root.lineno)
    for (_, statement) in root.children():
        if isinstance(statement, DeclStm):
            generic_root.add_variable(statement.to_generic_node())
        elif isinstance(statement, FuncDecl):
            generic_root.add_function(statement.to_generic_node())
        else:
            generic_root.main_stms.stmt_lst.append(statement.to_generic_node())
    return generic_root
