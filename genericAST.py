import cAST
import secrets

# to shift from OOP to procedural programming, we need to explicitly declare all objects 
list_declarations = []
str_declarations = []
class GenericNode:
    def __init__(self, lineno: int):
        self.lineno: int = lineno
    
    def children(self):
        raise NotImplementedError()

class FunctionDeclarations(GenericNode):
    def __init__(self, functions=[], lineno=0):
        self.functions = functions
        self.lineno = lineno
    
    def children(self):
        return tuple(("func[%d]" % i, var) for i, var in enumerate(self.functions))
    attr_names = ()

    def to_c_node(self) -> cAST.FunctionDeclarations:
        return default_conversion(self, cAST.FunctionDeclarations)
    
class FunctionDeclaration(GenericNode):
    def __init__(self, name="", params=None, ret_type=None, body=None, lineno=0, **kwargs):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.lineno = lineno
    
    def children(self):
        nodelist = [
            ('params', self.params),
            ('ret_type', self.ret_type),
            ('body', self.body)
        ]
        return tuple(nodelist)
    attr_names = ('name', )
    
    def to_c_node(self) -> cAST.FunctionDeclaration:
        return default_conversion(self, cAST.FunctionDeclaration)

class Function(GenericNode):
    def __init__(self, name, params, ret_type, body, lineno):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.lineno = lineno
    
    def children(self):
        nodelist = [
            ('params', self.params),
            ('ret_type', self.ret_type),
            ('body', self.body)
        ]
        return tuple(nodelist)
    attr_names = ('name', )

    def to_c_node(self) -> cAST.FunctionDeclaration:
        return default_conversion(self, cAST.FunctionDeclaration)

class FunctionCall(GenericNode):
    def __init__(self, name, params, lineno):
        self.name = name
        self.params = params
        self.lineno = lineno

    def children(self):
        nodelist = []
        if self.params is not None:
            nodelist.append(('params', self.params))
        return tuple(nodelist)
    attr_names = ('name', )

    def to_c_node(self) -> cAST.FunctionCall:
        return default_conversion(self, cAST.FunctionCall)

class ParameterList(GenericNode):
    def __init__(self, params, lineno):
        self.lineno = lineno
        self.params = params

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(('params[%d]' % i, child))
        return tuple(nodelist)
    attr_names = ()

    def to_c_node(self) -> cAST.ParameterList:
        return default_conversion(self, cAST.ParameterList)

class Parameter(GenericNode):
    def __init__(self, name, param_type, lineno):
        self.name = name
        self.param_type = param_type
        self.lineno = lineno
    
    def children(self):
        return (('type', self.param_type),)
    attr_names = ('name',)

    def to_c_node(self) -> cAST.Parameter:
        return default_conversion(self, cAST.Parameter)

class VariableDeclarations(GenericNode):
    def __init__(self, variables=[], lineno=0):
        self.variables = variables
        self.lineno = lineno
    
    def children(self):
        return tuple(("var[%d]" % i, var) for i, var in enumerate(self.variables))
    attr_names = ()

    def to_c_node(self) -> cAST.VariableDeclarations:
        return default_conversion(self, cAST.VariableDeclarations)

class VariableDeclaration(GenericNode):
    def __init__(self, name, var_type, lineno=0):
        self.name = name
        self.var_type = var_type
        self.lineno = lineno
        
    def children(self):
        return (("type", self.var_type),)
    
    attr_names = ("name",)
    
    def to_c_node(self) -> cAST.VariableDeclaration:
        return default_conversion(self, cAST.VariableDeclaration)

class IfStm(GenericNode):
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

    def to_c_node(self) -> cAST.IfStm:
        return default_conversion(self, cAST.IfStm)

class ElifBlock(IfStm):
    pass

class ElseBlock(GenericNode):
    def __init__(self, body, lineno):
        self.body = body
        self.lineno = lineno
    
    def children(self):
        return (('body', self.body),)
    attr_names = ()

    def to_c_node(self) -> cAST.ElseBlock:
        return default_conversion(self, cAST.ElseBlock)

class WhileStm(GenericNode):
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
    attr_names = ()

    def to_c_node(self) -> cAST.WhileStm:
        return default_conversion(self, cAST.WhileStm)

class RetStm(GenericNode):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno
    
    def children(self):
        return (('expr', self.expr),)
    attr_names = ()

    def to_c_node(self) -> cAST.RetStm:
        return default_conversion(self, cAST.RetStm)

class Constant(GenericNode):
    def __init__(self, const_type, value, lineno):
        self.const_type : Type = const_type
        self.value = value
        self.lineno = lineno

    def children(self):
        nodelist = []
        return tuple(nodelist)
    attr_names = ('type', 'value', )

    def to_c_node(self) -> cAST.Constant:
        const_type : Type = self.const_type
        value = self.value
        if const_type.name == 'bool':
            if value == "True":
                value = "1"
            else:
                value = "0"
        elif const_type.name == "id":
            return cAST.Constant(const_type.to_c_node(), value, self.lineno)
        elif const_type.name == "str":
            ref = "str_ref_"+secrets.token_hex(16)
            s = cAST.Constant(cAST.Type("id", 0), ref, 0)
            str_declarations.append((ref, value))
            return s

        return cAST.Cast(const_type.to_c_node(), cAST.Constant(const_type.to_c_node(), value, self.lineno), self.lineno)

class BinaryOperation(GenericNode):
    def __init__(self, op, left, right, lineno, **kwargs):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno

    def children(self):
        nodelist = []
        if self.left is not None:
            nodelist.append(('left', self.left))
        if self.right is not None:
            nodelist.append(('right', self.right))
        return tuple(nodelist)
    attr_names = ('op', )

    def to_c_node(self) -> cAST.BinaryOperation:
        op = self.op
        if op == "and":
            op = "&&"
            return cAST.Cast(cAST.Type("short", self.lineno),
                        cAST.BinaryOperation(op, self.left.to_c_node(), self.right.to_c_node(), self.lineno),
                        self.lineno)
        if op == "or":
            op = "||"
            return cAST.Cast(cAST.Type("short", self.lineno),
                        cAST.BinaryOperation(op, self.left.to_c_node(), self.right.to_c_node(), self.lineno),
                        self.lineno)
        if op == "concat_lists":
            param1 = self.left.to_c_node()
            param2 = self.right.to_c_node()
            params = cAST.ExpressionList([param1, param2], 0)
            call = cAST.FunctionCall("concat_lists", params, 0)
            return call
        if op == "concat_strings":
            param1 = self.left.to_c_node()
            param2 = self.right.to_c_node()
            params = cAST.ExpressionList([param1, param2], 0)
            call = cAST.FunctionCall("concat_strings", params, 0)
            return call
        return cAST.BinaryOperation(op, self.left.to_c_node(), self.right.to_c_node(), self.lineno)

class UnaryOperation(GenericNode):
    def __init__(self, op, expr, lineno):
        self.op = op
        self.expr = expr
        self.lineno = lineno
    
    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(('expr', self.expr))
        return tuple(nodelist)
    attr_names = ('op', )

    def to_c_node(self) -> cAST.UnaryOperation:
        op = self.op
        if op == "not":
            op = "!"
            return cAST.Cast(cAST.Type("short", self.lineno),
                cAST.UnaryOperation(op, self.expr.to_c_node(), self.lineno), self.lineno)
        return cAST.UnaryOperation(op, self.expr.to_c_node(), self.lineno)

class ExpressionList(GenericNode):
    def __init__(self, exprs, lineno):
        self.exprs = exprs
        self.lineno = lineno
    
    def children(self):
        nodelist = []
        if self.exprs is not None:
            nodelist.extend(("expr[%d]" % i, expr) for i, expr in enumerate(self.exprs))
        return  nodelist
    attr_names = ()

    def to_c_node(self) -> cAST.ExpressionList:
        return default_conversion(self, cAST.ExpressionList)

class List(GenericNode):
    def __init__(self, expr_list, lineno):
        self.expr_list = expr_list
        self.lineno = lineno
    
    def children(self):
        nodelist = (("expr_list", self.expr_list),)
        return nodelist
    attr_names = ()

    def to_c_node(self) -> cAST.List:
        l = default_conversion(self, cAST.List)
        list_declarations.append(l)
        return l

class Index(GenericNode):
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
    attr_names = ()

    def to_c_node(self) -> cAST.Index:
        params = cAST.ParameterList([self.expr.to_c_node(), self.expr_pos.to_c_node()], 0)
        if (self.etype.name == "int"):
            return cAST.FunctionCall("getInt", params, 0)
        if (self.etype.name == "list"):
            return  cAST.FunctionCall("getList", params, 0)
        if (self.etype.name == "bool"):
            return cAST.FunctionCall("getShort", params, 0)
        if (self.etype.name == "str"):
            return cAST.FunctionCall("getString", params, 0)
        raise NotImplementedError()

class Slice(GenericNode):
    def __init__(self, start, step, expr, end, lineno):
        self.start = start
        self.step = step
        self.expr = expr
        self.end = end
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

    def to_c_node(self) -> cAST.Index:
        params = cAST.ParameterList([self.expr.to_c_node(),
                                     self.start.to_c_node(),
                                     self.end.to_c_node(),
                                     self.step.to_c_node()], 0)
        return cAST.FunctionCall("slice", params, 0)

class Type(GenericNode): 
    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno
    
    def children(self):
        nodelist = []
        return tuple(nodelist)
    attr_names = ('name', )

    def to_c_node(self) -> cAST.Type:
        t = self
        if self.name == "bool":
            t = Type("short", lineno=self.lineno)
        if self.name == "list":
            t = Type("struct List *", 0) 
        if self.name == "str":
            t = Type("String *", 0) 
        return default_conversion(t, cAST.Type)

class StmList(GenericNode):
    def __init__(self, stmt_lst, lineno):
        self.stmt_lst = stmt_lst
        self.lineno = lineno

    def children(self):
        nodelist = []
        for i, stmt in enumerate(self.stmt_lst or []):
            nodelist.append(('stmt[%d]' % i, stmt))
        return nodelist
    attr_names = ()

    def transform(self, child):
        list_declarations.clear()
        str_declarations.clear()
        node = child.to_c_node()
        return list_declarations, str_declarations, node
    
    def to_c_node(self) -> cAST.StmList:
        statements = []
        for stm in self.stmt_lst:
            lists, strings, node = self.transform(stm)
            for ref, value in strings:
                statements.append(cAST.VariableDeclaration(ref, cAST.Type("String *", 0), lineno=self.lineno))
                statements.append(cAST.AssignStm(ref, 
                                  cAST.FunctionCall("new_string", cAST.ParameterList([], self.lineno), self.lineno),
                                  self.lineno))
                for v in value:
                    f = cAST.FunctionCall("stringInsert",
                                          cAST.ParameterList([cAST.Constant(cAST.Type("id", 0), ref, 0), cAST.Constant(cAST.Type("char", 0), v, 0)], self.lineno),
                                          0)
                    statements.append(f)
            for l in lists:
                list_type = cAST.Type('struct List *', lineno=self.lineno)
                statements.append(cAST.VariableDeclaration(l.identifier, list_type, lineno=self.lineno))
                statements.append(cAST.AssignStm(l.identifier, 
                                  cAST.FunctionCall("new_list", cAST.ParameterList([], self.lineno), self.lineno),
                                  self.lineno))
                statements.extend(l.to_c_init())
            statements.append(node)
        return cAST.StmList(statements, lineno=self.lineno)

class AssignStm(GenericNode):
    def __init__(self, name, expr, lineno):
        self.name = name
        self.expr = expr
        self.lineno = lineno
    
    def children(self):
        return (('expr', self.expr),)
    attr_names= ()

    def to_c_node(self) -> cAST.AssignStm:
        return default_conversion(self, cAST.AssignStm)

class Program(GenericNode):
    """
    Keeps track of generic program components, such as global variable and function declarations and main code
    """
    def __init__(self, main_stms=None, global_vars=None, functions=None, lineno=1):
        if main_stms is None:
            main_stms = StmList(stmt_lst=[], lineno=0)
        if global_vars is None:
            global_vars = VariableDeclarations([], lineno)
        if functions is None:
            functions = FunctionDeclarations([], lineno)
        self.main_stms = main_stms
        self.global_vars : VariableDeclarations = global_vars
        self.functions = functions
        self.lineno = lineno
    
    def add_variable(self, variable: "VariableDeclaration"):
        self.global_vars.variables.append(variable)
    
    def add_function(self, function: "FunctionDeclaration"):
        self.functions.functions.append(function)
    
    def children(self):
        return (('main_stms', self.main_stms),
                ('global_vars', self.global_vars),
                ('functions', self.functions))
    attr_names = ()

    def to_c_node(self) -> cAST.Program:
        c_root = cAST.Program(lineno=self.lineno, 
                          global_vars=self.global_vars.to_c_node(),
                          functions=self.functions.to_c_node())
        main_params = cAST.ParameterList([
                                     cAST.Parameter("argc", cAST.Type("int", 0), 0), 
                                     cAST.Parameter("argv", cAST.Type("char**", 0), 0)
                                    ], 0)
        main = cAST.FunctionDeclaration(name="main", 
                                   params=main_params, 
                                   ret_type=cAST.Type("void", 0), 
                                   body=self.main_stms.to_c_node())
        c_root.add_function(main)
        return c_root

def default_conversion(node: GenericNode, cNodeClass) -> cAST.CNode:
    kwargs = node.__dict__
    for k,v in kwargs.items():
        if isinstance(v, GenericNode):
            kwargs[k] = v.to_c_node()
        elif isinstance(v, list):
            els = []
            for el in v:
                if isinstance(el, GenericNode):
                    els.append(el.to_c_node())
                else:
                    els.append(el)
            kwargs[k] = els
    return cNodeClass(**kwargs)
