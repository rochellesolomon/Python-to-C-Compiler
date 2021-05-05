#!/usr/bin/env python3

import argparse
from ply import lex

# List of token names. This is always required
tokens = [
    'DECIMAL',
    'STRING',
    'ID',
    'PLUS',
    'MINUS',
    'TIMES',
    'INTDIVIDE', # //
    'DIVIDE',
    'MOD',
    'LESS',
    'LESSEQ',
    'ARROW',  # ->
    'GREATER',
    'GREATEREQ',
    'EQOP',
    'NEQ',
    'COLON',
    'COMMA',
    'SEMICO',
    'PERIOD',
    'EQ',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'LCBRACK',
    'RCBRACK',
    'QUOTATION',
]

# Reserved words which should not match any IDs
reserved = {
    'def' : 'DEF',
    'int' : 'INT',
    'bool' : 'BOOLEAN',
    'str' : 'STR',
    'list' : 'LIST',
    'True' : 'TRUE',
    'False' : 'FALSE',
    'and' : 'AND',
    'or' : 'OR',
    'if' : 'IF',
    'elif' : 'ELIF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'return' : 'RETURN',
    'not' : 'NOT'
}

# Add reserved names to list of tokens
tokens += list(reserved.values())

class pythonLexer():
    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Regular expression rule with some action code
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_INTDIVIDE = r'//'
    t_DIVIDE = r'/'
    t_MOD = r'\%'
    t_LESSEQ = r'\<='
    t_LESS = r'\<'
    t_ARROW = r'\->'
    t_GREATEREQ = r'\>='
    t_GREATER = r'\>'
    t_EQOP = r'\=='
    t_NEQ = r'\!='
    t_COLON = r'\:'
    t_COMMA = r','
    t_SEMICO = r'\;'
    t_PERIOD = r'\.'
    t_EQ = r'\='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACK = r'\['
    t_RBRACK = r'\]'
    t_LCBRACK = r'\{'
    t_RCBRACK = r'\}'
    t_QUOTATION = r'\"'

    # A regular expression rule with some action code
    def t_DECIMAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'ID') # Check for reserved words
        return t

    def t_STRING(self, t):
        r'"[^\"]*"'
        t.value = t.value[1:-1]
        return t

    # Define a rule so we can track line numbers. DO NOT MODIFY
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Error handling rule. DO NOT MODIFY
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer. DO NOT MODIFY
    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = lex.lex(module=self, **kwargs)

    # Test the output. DO NOT MODIFY
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

# Main function. DO NOT MODIFY
if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Take in the python source code and perform lexical analysis.')
    parser.add_argument('FILE', help="Input file with python source code")
    args = parser.parse_args()

    f = open(args.FILE, 'r')
    data = f.read()
    f.close()

    m = pythonLexer()
    m.build()
    m.test(data)
