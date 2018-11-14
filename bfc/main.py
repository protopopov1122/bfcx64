from bfc.Token import brainfuck_tokenize
from bfc.Parser import brainfuck_parse
from bfc.IROptimizer import brainfuck_ir_optimize
from bfc.FlowAnalysis import brainfuck_ir_analyze_flow
from bfc.Codegen import Codegen
from bfc.Error import BrainfuckError
from bfc.Options import *
import io
import sys
import os


CELL_SIZE = {
    'byte': MemoryCellSize.Byte,
    'word': MemoryCellSize.Word,
    'dword': MemoryCellSize.DWord,
}

MEMORY_MODEL = {
    'wrap': MemoryOverflow.Wrap,
    'abort': MemoryOverflow.Abort,
    'undefined': MemoryOverflow.Undefined
}


def parse_args(args):
    file_name = None
    codegen = Codegen['x64-linux']
    params = dict()
    for arg in args[1:]:
        if '=' in arg:
            key = arg.split('=')[0]
            value = arg.split('=')[1]
            params[key] = value
        elif file_name is None:
            file_name = arg
        elif arg in Codegen:
            codegen = Codegen[arg]
        else:
            raise BrainfuckError(f'Code generator {arg} not found')

    cell_size = MemoryCellSize.Byte
    memory_model = MemoryOverflow.Wrap
    if 'cell' in params and params['cell'] in CELL_SIZE:
        cell_size = CELL_SIZE[params['cell']]
    if 'memory' in params and params['memory'] in MEMORY_MODEL:
        memory_model = MEMORY_MODEL[params['memory']]
    return file_name, codegen, memory_model, cell_size


def main(args):
    if len(args) < 2:
        print('Provide file name')
    else:
        file_name, codegen, memory_model, cell_size = parse_args(args)
        with open(file_name) as code:
            module_name = os.path.basename(code.name).split('.')[0]
            options = BrainfuckOptions(module_name, memory_overflow=memory_model, cell_size=cell_size)
            asm = io.StringIO()
            ir = brainfuck_parse(brainfuck_tokenize(code))
            ir = brainfuck_ir_optimize(ir)
            ir = brainfuck_ir_analyze_flow(ir)
            codegen(asm, ir, options)
            # print('\n'.join([str(instr) for instr in ir.get_body()]))
            print(asm.getvalue())



if __name__ == '__main__':
    main(sys.argv)
