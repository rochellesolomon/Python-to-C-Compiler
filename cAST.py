import secrets

class CNode:
    def __init__(self, lineno: int):
        self.lineno: int = lineno
    
    def children(self):
        raise NotImplementedError()

    def to_code(self):
        raise NotImplementedError()

class FunctionDeclarations(CNode):
    def __init__(self, functions=[], lineno=0):
        self.functions = functions
        self.lineno = lineno

    
    def children(self):
        return tuple(("func[%d]" % i, var) for i, var in enumerate(self.functions))
    
    def to_code(self):
        return '\n'.join(f.to_code() for f in self.functions)
    attr_names = ()
    
class FunctionDeclaration(CNode):
    def __init__(self, name="", params=None, ret_type=None, body=None, lineno=0):
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

    def to_code(self):
        return f"{self.ret_type.to_code()} {self.name}({self.params.to_code()}) {{\n{self.body.to_code()}\n}}\n"

class FunctionCall(CNode):
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
    def to_code(self):
        return f"{self.name}({self.params.to_code()})"

class ParameterList(CNode):
    def __init__(self, params, lineno):
        self.lineno = lineno
        self.params = params

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(('params[%d]' % i, child))
        return tuple(nodelist)
    attr_names = ()
    def to_code(self):
        if self.params:
            return ", ".join(p.to_code() for p in self.params)
        return ""

class Parameter(CNode):
    def __init__(self, name, param_type, lineno):
        self.name = name
        self.param_type = param_type
        self.lineno = lineno
    
    def children(self):
        return (('type', self.param_type),)
    attr_names = ('name',)
    def to_code(self):
        return f"{self.param_type.to_code()} {self.name}"

class VariableDeclarations(CNode):
    def __init__(self, variables=[], lineno=0):
        self.variables = variables
        self.lineno = lineno
    
    def children(self):
        return tuple(("var[%d]" % i, var) for i, var in enumerate(self.variables))
    attr_names = ()
    def to_code(self):
        return ", ".join(v.to_code() for v in self.variables)

class VariableDeclaration(CNode):
    def __init__(self, name, var_type, lineno=0):
        self.name = name
        self.var_type = var_type
        self.lineno = lineno
        
    def children(self):
        return (("type", self.var_type),)
    
    attr_names = ("name",)
    def to_code(self):
        return f"{self.var_type.to_code()} {self.name}"

class IfStm(CNode):
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
    def to_code(self):
        ret = f"if ({self.cond.to_code()}) {{\n{self.body.to_code()}\n}}"
        if self.else_branch is not None:
            ret += self.else_branch.to_code()
        return ret

class ElifBlock(IfStm):
    def to_code(self):
        ret = f"else if ({self.cond.to_code()}) {{\n{self.body.to_code()}\n}}"
        if self.else_branch is not None:
            ret += self.else_branch.to_code()
        return ret
        

class ElseBlock(CNode):
    def __init__(self, body, lineno):
        self.body = body
        self.lineno = lineno
    
    def children(self):
        return (('body', self.body),)
    attr_names = ()
    def to_code(self):
        return f"else {{\n{self.body.to_code()}\n}}"

class WhileStm(CNode):
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
    def to_code(self):
        return f"while ({self.cond.to_code()}) {{\n{self.body.to_code()}\n}}"

class RetStm(CNode):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno
    
    def children(self):
        return (('expr', self.expr),)
    attr_names = ()
    def to_code(self):
        return f"return {self.expr.to_code()}"

class Constant(CNode):
    def __init__(self, type, value, lineno):
        self.type = type
        self.value = value
        self.lineno = lineno

    def children(self):
        nodelist = []
        return tuple(nodelist)
    attr_names = ('type', 'value', )

    def to_code(self):
        if self.type.name == "char":
            return f"'{self.value}'"
        return str(self.value)

class BinaryOperation(CNode):
    def __init__(self, op, left, right, lineno):
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

    def to_code(self):
        return f"({self.left.to_code()} {self.op} {self.right.to_code()})"

class UnaryOperation(CNode):
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

    def to_code(self):
        return f"{self.op} {self.expr.to_code()}"

class ExpressionList(CNode):
    def __init__(self, exprs, lineno):
        self.exprs = exprs
        self.lineno = lineno
    
    def children(self):
        nodelist = []
        if self.exprs is not None:
            nodelist.extend(("expr[%d]" % i, expr) for i, expr in enumerate(self.exprs))
        return  nodelist
    attr_names = ()
    def to_code(self):
        if self.exprs is not None:
            return ", ".join(e.to_code() for e in self.exprs)
        return ""

class List(CNode):
    def __init__(self, expr_list, lineno):
        self.expr_list = expr_list
        self.lineno = lineno
        self.identifier = "list_def_"+secrets.token_hex(16)
        self.ref = Constant(Type("id", lineno=self.lineno), self.identifier, lineno=self.lineno)
    
    def children(self):
        # nodelist = (("expr_list", self.expr_list),)
        # return nodelist
        return ()
    
    def to_c_init(self):
        statements = []
        if self.expr_list.exprs:
            for expr in self.expr_list.exprs:
                params = ParameterList([self.ref, expr], self.lineno)
                statements.append(FunctionCall("push", params, self.lineno))
        return statements
    
    def to_code(self):
        return self.ref.to_code()
    attr_names = ()

class Index(CNode):
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

    def to_code(self):
        pass

class Type(CNode): 
    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno
    
    def children(self):
        nodelist = []
        return tuple(nodelist)
    attr_names = ('name', )

    def to_code(self):
        return self.name

class StmList(CNode):
    def __init__(self, stmt_lst, lineno):
        self.stmt_lst = stmt_lst
        self.lineno = lineno

    def children(self):
        nodelist = []
        for i, stmt in enumerate(self.stmt_lst or []):
            nodelist.append(('stmt[%d]' % i, stmt))
        return nodelist
    attr_names = ()
    def to_code(self):
        pass
        return "\n".join(s.to_code()+";" for s in self.stmt_lst)

class AssignStm(CNode):
    def __init__(self, name, expr, lineno):
        self.name = name
        self.expr = expr
        self.lineno = lineno
    
    def children(self):
        return (('expr', self.expr),)
    attr_names= ()

    def to_code(self):
        return f"{self.name} = {self.expr.to_code()}"

class Cast(CNode):
    def __init__(self, type, expr, lineno):
        self.type = type
        self.expr = expr
        self.lineno = lineno
    
    def children(self):
        nodelist = [
            ('type', self.type),
            ('expr', self.expr)
        ]
        return tuple(nodelist)

    attr_names = ()
    
    def to_code(self):
        return f"({self.type.to_code()}) ({self.expr.to_code()})"

class Reference(CNode):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno
        
    def children(self):
        return (('expr', self.expr),)
    attr_names = ()

    def to_code(self):
        return f"&({self.expr})"

class Dereference(CNode):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno

    def children(self):
        return (('expr', self.expr),)
    attr_names = ()

    def to_code(self):
        return f"*({self.expr})"

class Program(CNode):
    """
    Keeps track of C program components, such as global variable and function declarations
    """
    def __init__(self, global_vars=None, functions=None, lineno=1, **kwargs):
        if global_vars is None:
            global_vars = VariableDeclarations([], lineno)
        if functions is None:
            functions = FunctionDeclarations([], lineno)
        self.global_vars : VariableDeclarations = global_vars
        self.functions = functions
        self.lineno = lineno
    
    def add_variable(self, variable: "VariableDeclaration"):
        self.global_vars.variables.append(variable)
    
    def add_function(self, function: "FunctionDeclaration"):
        self.functions.functions.append(function)
    
    def children(self):
        return (('global_vars', self.global_vars),
                ('functions', self.functions))
    attr_names = ()

    def to_code(self):
        ret = "#include \"python_print.h\"\n" + \
              "#include \"python_list.h\"\n" + \
              "#include \"python_string.h\"\n" + \
              "#include \"slicing.h\"\n"
        for variable in self.global_vars.variables:
            ret += f"{variable.to_code()};\n"
        
        funcs = ""
        for function in self.functions.functions:
            funcs += function.to_code()

        return ret + funcs

