#!/usr/bin/env python3

import argparse
import os
import shutil
from ply import yacc
import pythonAST as ast

# Get the token map from the lexer. This is required.
from pythonScanner import tokens, pythonLexer


class pythonParser:
    precedence = (
        ('left', 'AND'),
        ('left', 'EQOP', 'NEQ'),
        ('left', 'LESS', 'LESSEQ', 'GREATER', 'GREATEREQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        # ('right', 'UNARY')
    )

    '''
    Let the parser know that symbol "stm_list_or_empty" is the starting point
    '''
    start = 'stm_list_or_empty'

    '''
    Statement list
    '''

    def p_stm_list_or_empty(self, p):
        '''
        stm_list_or_empty : stm_list
                          | empty
        '''
        p[0] = ast.StmList(p[1], p.lineno(1))

    def p_stm_list(self, p):
        '''
        stm_list : stm_list stm
                     | stm
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_stm(self, p):
        '''
        stm : func_decl
            | if_stm
            | while_stm
            | decl_stm SEMICO
            | assign_stm SEMICO
            | ret_stm SEMICO
            | expr SEMICO
            | SEMICO
        '''
        p[0] = p[1]

    def p_decl_stm(self, p):
        '''
        decl_stm : ID COLON type
        '''
        p[0] = ast.DeclStm(p[1], p[3], p.lineno(1))

    def p_assign_stm(self, p):
        '''
        assign_stm : ID EQ expr
        '''
        p[0] = ast.AssignStm(p[1], p[3], p.lineno(1))

    def p_if_stm(self, p):
        '''
        if_stm : IF expr COLON body else_block_or_empty
                    | IF expr COLON body elif_block
        '''
        p[0] = ast.IfStm(p[2], p[4], p[5], p.lineno(1))

    def p_elif_block(self, p):
        '''
        elif_block : ELIF expr COLON body else_block_or_empty
                       | ELIF expr COLON body elif_block
        '''
        p[0] = ast.ElifBlock(p[2], p[4], p[5], p.lineno(1))

    def p_else_block_or_empty(self, p):
        '''
        else_block_or_empty : else_block
                                | empty
        '''
        p[0] = p[1]

    def p_else_block(self, p):
        '''
        else_block : ELSE COLON body
        '''
        p[0] = ast.ElseBlock(p[3], p.lineno(1))

    def p_while_stm(self, p):
        '''
        while_stm : WHILE expr COLON body
        '''
        p[0] = ast.WhileStm(p[2], p[4], p.lineno(1))

    def p_return_stm(self, p):
        '''
        ret_stm : RETURN expr
        '''
        p[0] = ast.RetStm(p[2], p.lineno(1))

    def p_brackets_expr(self, p):
        '''
        expr : LPAREN expr RPAREN
        '''
        p[0] = p[2]

    def p_binary_ops(self, p):
        '''
        expr : expr PLUS expr
             | expr MINUS expr 
             | expr TIMES expr
             | expr INTDIVIDE expr
             | expr DIVIDE expr
             | expr MOD expr
             | expr LESS expr
             | expr LESSEQ expr
             | expr GREATER expr
             | expr GREATEREQ expr
             | expr EQOP expr
             | expr NEQ expr
             | expr AND expr
             | expr OR expr
        '''
        p[0] = ast.BinOp(p[2], p[1], p[3], p.lineno(2))

    def p_unary_ops(self, p):
        '''
        expr : NOT expr
             | MINUS expr
        '''
        p[0] = ast.UnaryOp(p[1], p[2], p.lineno(1))

    def p_func_call(self, p):
        '''
        expr : ID LPAREN expr_list_or_empty RPAREN
        '''
        p[0] = ast.FuncCall(p[1], p[3], p.lineno(1))

    def p_number(self, p):
        '''
        expr : DECIMAL
        '''
        p[0] = ast.Constant(ast.Type('int', p.lineno(1)), p[1], p.lineno(1))

    def p_boolean(self, p):
        '''
        expr : TRUE 
             | FALSE
        '''
        p[0] = ast.Constant(ast.Type('bool', p.lineno(1)), p[1], p.lineno(1))

    def p_string(self, p):
        '''
        expr : STRING
        '''
        p[0] = ast.Constant(ast.Type("str", p.lineno(1)), p[1], p.lineno(1))
    
    def p_string_or_empty(self, p):
        '''
        string_or_empty : STRING
                        | empty
        '''
        if p[1] is None:
            p[0] = ""
        else:
            p[0] = p[1]

    def p_list_expr(self, p):
        '''
        expr : list
        '''
        p[0] = p[1]

    def p_id_expr(self, p):
        '''
        expr : ID
        '''
        p[0] = ast.Constant(ast.Type('id', p.lineno(1)), p[1], p.lineno(1))

    def p_list(self, p):
        '''
        list : LBRACK expr_list_or_empty RBRACK
        '''
        p[0] = ast.List(p[2], p.lineno(1))

    def p_list_index(self, p):
        '''
        expr : type LPAREN expr LBRACK expr RBRACK RPAREN
        '''
        p[0] = ast.Index(p[1], p[3], p[5], p.lineno(1))

    def p_slice_expression(self, p):
        '''
        expr : expr LBRACK slice RBRACK
             | expr LBRACK slice_with_step RBRACK
        '''
        p[0] = ast.Slice(p[3][0], p[3][2], p[1], p[3][1], p.lineno(1))

    def p_slice(self, p):
        '''
        slice : slice_index_or_none COLON slice_index_or_none
        '''
        p[0] = (p[1], p[3], None)

    def p_slice_with_step(self, p):
        '''
        slice_with_step : slice COLON slice_index_or_none
        '''
        p[0] = (p[1][0], p[1][1], p[3])

    def p_slice_index_or_none(self, p):
        '''
        slice_index_or_none : expr
                            | empty
        '''
        p[0] = p[1]

    def p_expr_list_or_empty(self, p):
        '''
        expr_list_or_empty : expr_list 
                           | empty
        '''
        p[0] = ast.ExprList(p[1], p.lineno(1))

    def p_expr_list(self, p):
        '''
        expr_list : expr_list COMMA expr 
                  | expr
        '''
        if (len(p) == 2):
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_func_decl(self, p):
        '''
        func_decl : DEF ID LPAREN func_params_or_empty RPAREN ARROW type COLON body
        '''
        p[0] = ast.FuncDecl(p[2], p[4], p[7], p[9], p.lineno(1))

    def p_func_params_or_empty(self, p):
        '''
        func_params_or_empty : func_params
                             | empty
        '''
        p[0] = ast.ParamList(p[1], p.lineno(1))

    def p_func_params(self, p):
        '''
        func_params : func_params COMMA param
                    | param
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_func_param(self, p):
        '''
        param : ID COLON type
        '''
        p[0] = ast.Param(p[1], p[3], p.lineno(1))

    def p_body(self, p):
        '''
        body : LCBRACK stm_list_or_empty RCBRACK
        '''
        p[0] = p[2]
    
    def p_type(self, p):
        '''
        type : BOOLEAN
             | INT
             | LIST
             | STR
        '''
        p[0] = ast.Type(p[1], p.lineno(1))

    def p_empty(self, p):
        '''
        empty :
        '''
        pass

    def p_error(self, p):
        print("Syntax error at token", p)

    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = pythonLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    def test(self, data, out):
        result = self.parser.parse(data, tracking=True)
        visitor = ast.NodeVisitor()
        visitor.visit(result)
        with open(out, 'w') as f:
            f.write(visitor.toJSON(result))


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(
        description='Take in the python source code and parses it')
    argparser.add_argument(
        '-f', '--file', help='Input file with python source code', default=None)
    args = argparser.parse_args()

    m = pythonParser()
    m.build()

    if os.path.exists('out'):
        shutil.rmtree('out')
    os.mkdir('out')

    if args.file:
        with open(args.file, 'r') as f:
            data = f.read()
        m.test(data, os.path.join('out', os.path.split(args.file)[1]+'.json'))
    else:
        for d in os.listdir('examples'):
            with open(os.path.join('examples', d)) as f:
                data = f.read()
            name = os.path.split(d)[1]
            m.test(data, os.path.join('out', name+'.json'))
