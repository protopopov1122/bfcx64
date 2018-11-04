from bfc.Token import brainfuck_tokenize
from bfc.Parser import brainfuck_parse
from bfc.Optimize import brainfuck_optimize_ast
from bfc.x64.x64Codegen import x64Codegen
from bfc.Compiler import brainfuck_compile
import io
import sys


def main(args):
    if len(args) < 2:
        print('Provide file name')
    else:
        with open(args[1]) as code:
            asm = io.StringIO()
            ast = brainfuck_parse(brainfuck_tokenize(code))
            ast = brainfuck_optimize_ast(ast)
            codegen = x64Codegen(asm)
            brainfuck_compile(ast, codegen)
            with open('{}.asm'.format(args[1]), 'w') as output:
                output.write(asm.getvalue())



if __name__ == '__main__':
    main(sys.argv)
