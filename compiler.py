import argparse
import os
import shutil
from pythonParser import pythonParser
from pythonAST import python_ast_to_generic, NodeVisitor
from pythonTypeChecker import TypeChecker, ParseError

def run_compiler(m: pythonParser, data: str, file_name:str):
    python_ast = m.parser.parse(data, tracking=True)
    tc = TypeChecker()
    try:
        tc.typecheck(python_ast)
        generic_ast = python_ast_to_generic(python_ast)
        c_ast = generic_ast.to_c_node()
        with open(file_name, 'w') as f:
            f.write(c_ast.to_code())
    except ParseError as p:
        print(f"Error in file {file_name} {p}")

def main():
    argparser = argparse.ArgumentParser(description='Take in the python source code and parses it')
    argparser.add_argument('-f', '--file', help='Input file with python source code', default=None)
    args = argparser.parse_args()

    m = pythonParser()
    m.build()

    if os.path.exists('out'):
        shutil.rmtree('out')

    if args.file:
        shutil.copytree("c_libs", "out")
        with open(args.file, 'r') as f:
            data = f.read()
        file_name = os.path.basename(args.file)
        out_name = os.path.join("out", file_name+".c")
        run_compiler(m, data, out_name)
    else:
        os.mkdir("out")
        for d in os.listdir('examples'):
            example_folder = os.path.join("out", d)
            shutil.copytree("c_libs", example_folder)
            with open(os.path.join('examples', d)) as f:
                data = f.read()
            name = os.path.join(example_folder, os.path.split(d)[1]) + ".c"
            run_compiler(m, data, name)


if __name__ == "__main__":
    main()