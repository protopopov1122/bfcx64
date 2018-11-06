from bfc.Token import brainfuck_tokenize
from bfc.Parser import brainfuck_parse
from bfc.Optimize import brainfuck_optimize_ast
from bfc.IRCompiler import brainfuck_compile_ir
from bfc.IROptimizer import brainfuck_ir_optimize
from bfc.x64.x64Codegen import brainfuck_compile_x64
import io
import sys


def main(args):
    if len(args) < 2:
        print('Provide file name')
    else:
        with open(args[1]) as code:
            asm = io.StringIO()
            ast = brainfuck_parse(brainfuck_tokenize(code))
            ir = brainfuck_compile_ir(brainfuck_optimize_ast(ast))
            brainfuck_ir_optimize(ir)
            brainfuck_compile_x64(asm, ir)
            print(asm.getvalue())



if __name__ == '__main__':
    main(sys.argv)
