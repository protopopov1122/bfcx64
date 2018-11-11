from bfc.Token import brainfuck_tokenize
from bfc.Parser import brainfuck_parse
from bfc.Optimize import brainfuck_optimize_ast
from bfc.IRCompiler import brainfuck_compile_ir
from bfc.IROptimizer import brainfuck_ir_optimize
from bfc.Codegen import Codegen
from bfc.Error import BrainfuckError
import io
import sys


def main(args):
    if len(args) < 2:
        print('Provide file name')
    else:
        if len(args) == 3 and args[2] in Codegen:
            codegen = Codegen[args[2]]
        elif len(args) < 3:
            codegen = Codegen['x64']
        else:
            raise BrainfuckError('Code generator {} not found'.format(args[2]))
        with open(args[1]) as code:
            asm = io.StringIO()
            ast = brainfuck_parse(brainfuck_tokenize(code))
            ir = brainfuck_compile_ir(brainfuck_optimize_ast(ast))
            brainfuck_ir_optimize(ir)
            codegen(asm, ir)
            print(asm.getvalue())



if __name__ == '__main__':
    main(sys.argv)
