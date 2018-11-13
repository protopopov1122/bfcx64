from bfc.Token import brainfuck_tokenize
from bfc.Parser import brainfuck_parse
from bfc.IROptimizer import brainfuck_ir_optimize
from bfc.Codegen import Codegen
from bfc.Error import BrainfuckError
from bfc.Options import *
import io
import sys
import os


def main(args):
    if len(args) < 2:
        print('Provide file name')
    else:
        if len(args) == 3 and args[2] in Codegen:
            codegen = Codegen[args[2]]
        elif len(args) < 3:
            codegen = Codegen['x64-linux']
        else:
            raise BrainfuckError('Code generator {} not found'.format(args[2]))
        with open(args[1]) as code:
            module_name = os.path.basename(code.name).split('.')[0]
            options = BrainfuckOptions(module_name, memory_overflow=MemoryOverflow.Wrap, cell_size=MemoryCellSize.Byte)
            asm = io.StringIO()
            ir = brainfuck_parse(brainfuck_tokenize(code))
            ir = brainfuck_ir_optimize(ir)
            codegen(asm, ir, options)
            # print('\n'.join([str(instr) for instr in ir.get_body()]))
            print(asm.getvalue())



if __name__ == '__main__':
    main(sys.argv)
