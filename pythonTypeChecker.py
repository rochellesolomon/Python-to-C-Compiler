#!/usr/bin/env python3

from pythonSymbolTable import SymbolTable, ParseError
import pythonAST as ast

class TypeChecker(object):
    """
    Uses the same visitor pattern as ast.NodeVisitor, but modified to
    perform type checks, as well as to generate the symbol table.

    If the object is not associated with either symbol table or a type,
    then it will return None.

    Alternatively, you could implement a method which returns the
    type of the object in question into the Node object.
    """

    def typecheck(self, node, st=None):
        method = 'check_' + node.__class__.__name__
        return getattr(self, method, self.generic_typecheck)(node, st)

    def generic_typecheck(self, node, st=None):
        raise NotImplementedError(f"Typecheck not implemented for node type {node.__class__}")

    def eq_type(self, t1, t2):
        """
        Helper function to check if two given type node is that of the
        same type. Precondition is that both t1 and t2 are that of class Type
        """
        if not isinstance(t1, ast.Type) or not isinstance(t2, ast.Type):
            raise ParseError("eq_type invoked on non-type objects")
        if t1.name == "any" or t2.name == "any":
            return True
        return t1.name == t2.name

    def check_FuncDecl(self, node, st: SymbolTable):
        st.push_scope()
        if node.params is not None:
            self.typecheck(node.params, st)
        if node.body is not None:
            self.typecheck(node.body, st)
        
        for return_stm in node.ret_stms:
            ret_stmt_type = self.typecheck(return_stm, st)
            if not self.eq_type(ret_stmt_type, node.ret_type):
                raise ParseError("Mismatch of return type within function \"" + node.name + "\"", node.lineno)
        st.pop_scope()

        st.declare_function(node.name, node, node.lineno)
        
        return node.ret_type
    
    def check_FuncCall(self, node, st):
        function = st.lookup_function(node.name ,node.lineno)

        if len(function.params.params or []) != len(node.params.exprs or []):
            raise ParseError("Argument length mismatch with function", node.lineno)

        for i, arg in enumerate(node.params.exprs or []):
            arg_type = self.typecheck(arg, st)
            if not self.eq_type(arg_type, function.params.params[i].param_type):
                raise ParseError("Argument type mismatch with function parameter", node.lineno)

        return function.ret_type

    
    def check_AssignStm(self, node, st):

        var_type = st.lookup_variable(node.name, node.lineno)
        expr_type = self.typecheck(node.expr, st)
        if not self.eq_type(var_type, expr_type):
            raise ParseError("Variable \"" + node.name + "\" has the type",
                             var_type.name, "but is being assigned the type",
                             expr_type.name, node.lineno)

        return expr_type

    def check_BinOp(self, node: ast.BinOp, st):
        left_type : ast.Type = self.typecheck(node.left, st)
        right_type : ast.Type = self.typecheck(node.right, st)
        if not self.eq_type(left_type, right_type):
            raise ParseError("Left and right expressions are of different type", node.lineno)
        bad_op_err = ParseError(f"Cannot apply operation {node.op} to types "+
                                 f"{left_type.name}, {right_type.name}", node.lineno)
        if node.op == "+" and self.eq_type(left_type, ast.Type("list")):
            node.inferred_type = ast.Type("list")
            node.op = "concat_lists"
            return ast.Type("list")
        if node.op == "+" and self.eq_type(left_type, ast.Type("str")):
            node.inferred_type = ast.Type("str")
            node.op = "concat_strings"
            return ast.Type("str")
        if node.op in ['+', '-', '*', '/', '%']:
            if self.eq_type(left_type, ast.Type('int')):
                node.inferred_type = ast.Type("int")
                return ast.Type("int")
            raise bad_op_err
        if node.op in ["<", "<=", ">", ">="]:
            if self.eq_type(left_type, ast.Type("int")):
                node.inferred_type = ast.Type("bool")
                return ast.Type("bool")
            raise bad_op_err
        if node.op == '==':
            return ast.Type('bool')
        if node.op in ['and', 'or']:
            if self.eq_type(left_type, ast.Type('bool')):
                node.inferred_type = ast.Type("bool")
                return ast.Type('bool')
            raise bad_op_err

        raise NotImplementedError(node.op)

    def check_Constant(self, node, st):
        """
        Returns the type of the constant. If the constant refers to
        some kind of id, then we need to find if the id has been declared.
        """
        if self.eq_type(node.const_type, ast.Type('id')):
            return st.lookup_variable(node.value, node.lineno)
        return node.const_type

    def check_DeclStm(self, node, st):
        st.declare_variable(node.name, node.var_type, node.lineno)
        return None

    def check_IfStm(self, node: ast.IfStm, st):
        """
        Check if the condition expression is a boolean or integer type, then
        recursively typecheck all of if statement body.

        Note that most of the programming languages, such as C, Java, and
        Python, all accepts ints/floats for conditions as well. That is
        something you should consider for your project.
        """

        cond_type = self.typecheck(node.cond, st)
        if not self.eq_type(ast.Type('bool'), cond_type) and not self.eq_type(ast.Type('int'), cond_type):
            raise ParseError("If statement requires boolean or integer as its condition", node.lineno)

        if node.body is not None:
            self.typecheck(node.body, st)
        if node.else_branch is not None:
            self.typecheck(node.else_branch, st)

        return None
    
    def check_ElifBlock(self, node: ast.ElifBlock, st):
        cond_type = self.typecheck(node.cond, st)
        if not self.eq_type(ast.Type('bool'), cond_type) and not self.eq_type(ast.Type('int'), cond_type):
            raise ParseError("If statement requires boolean as its condition", node.lineno)

        if node.body is not None:
            self.typecheck(node.body, st)
        if node.else_branch is not None:
            self.typecheck(node.else_branch, st)


    def check_ElseBlock(self, node:ast.ElseBlock, st):
        self.typecheck(node.body, st)


    def check_ParamList(self, node: ast.ParamList, st):
        """
        Add all of the parameters to the symbol table
        """
        if node.params:
            for param in node.params:
                st.declare_variable(param.name, param.param_type, param.lineno)
        return None

    def check_RetStm(self, node, st):
        return self.typecheck(node.expr, st)

    def check_StmList(self, node, st):
        """
        In python, statement lists do not create new scope
        """
        if st is None:
            st = SymbolTable()
        if node.stmt_lst:
            for stmt in node.stmt_lst:
                self.typecheck(stmt, st)

        # List itself does not have any type
        return None

    def check_Type(self, node, st):
        return node

    def check_UnaryOp(self, node: ast.UnaryOp, st):
        """
        NOTE
        Similar to BinOp, you should check if the unary operator is
        applicable with the type returned by the expression
        (i.e., '-' could only make sense if the expression is an integer)
        """
        expr_type = self.typecheck(node.expr, st)
        type_err = ParseError(f"Operation {node.op} cannot be applied to {expr_type.name}", node.lineno)
        if node.op == "not":
            if self.eq_type(expr_type, ast.Type("bool")):
                return expr_type
            raise type_err
        if node.op == "-":
            if self.eq_type(expr_type, ast.Type("int")):
                return expr_type
            raise type_err

    def check_WhileStm(self, node: ast.WhileStm, st):
        """
        First, check if the condition returns the type boolean or integer.
        Then, push another scope into the scope stack and perform typecheck
        within the while statement body.
        """

        cond_type = self.typecheck(node.cond, st)
        if not self.eq_type(ast.Type('bool'), cond_type) and not self.eq_type(ast.Type('int'), cond_type):
            raise ParseError("While statement requires boolean or integer as its condition", node.lineno)

        if node.body is not None:
            self.typecheck(node.body, st)

        return None
    
    def check_List(self, node: ast.List, st):
        if node.expr_list and node.expr_list.exprs:
            for e in node.expr_list.exprs:
                self.typecheck(e, st)
        return ast.Type("list")

    def check_Index(self, node: ast.Index, st):
        expr_type = self.typecheck(node.expr, st)
        index_type = self.typecheck(node.expr_pos, st)
        if  not self.eq_type(expr_type, ast.Type("list")) and \
            not self.eq_type(expr_type, ast.Type("str")):
            raise ParseError("Indexed expression must iterable", node.lineno)
        if not self.eq_type(index_type, ast.Type("int")):
            raise ParseError("List index must be an int", node.lineno)
        return node.etype
    
    def check_Slice(self, node: ast.Slice, st):
        intT = ast.Type("int")
        if  not self.eq_type(intT, self.typecheck(node.start, st)) or \
            not self.eq_type(intT, self.typecheck(node.end, st)) or \
            not self.eq_type(intT, self.typecheck(node.step, st)):
            raise ParseError("Slice index must be an int", node.lineno)
        exprType = self.typecheck(node.expr, st)
        if  not self.eq_type(exprType, ast.Type("list")) and \
            not self.eq_type(exprType, ast.Type("str")):
            raise ParseError("Slicing requires an iterable type")
        return exprType