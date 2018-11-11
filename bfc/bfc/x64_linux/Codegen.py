import os
from bfc.IR import *


def _dump_runtime(output):
    with open(os.path.join(os.path.dirname(__file__), 'runtime.asm')) as runtime:
        output.write(runtime.read())
        output.write('\n')


def _x64_add(output, block: BrainfuckIRBlock, instr: BrainfuckIRInstruction):
    output.write('\tadd byte [rbx + r12], {}\n'.format(instr.get_argument()))


def _x64_set(output, block: BrainfuckIRBlock, instr: BrainfuckIRInstruction):
    output.write('\tmov byte [rbx + r12], {}\n'.format(instr.get_argument()))


def _x64_shift(output, block: BrainfuckIRBlock, instr: BrainfuckIRInstruction):
    output.write('\tadd r12, {}\n'.format(instr.get_argument()))
    output.write('\tcall _bf_normalize_pointer\n')


def _x64_write(output, block: BrainfuckIRBlock, instr: BrainfuckIRInstruction):
    output.write('\tcall _bf_write\n')


def _x64_read(output, block: BrainfuckIRBlock, instr: BrainfuckIRInstruction):
    output.write('\tcall _bf_read\n')


def _x64_branch(output, block: BrainfuckIRBlock, instr: BrainfuckIRInstruction):
    destination = instr.get_argument()
    if isinstance(destination, int):
        if block.get_id() + 1 != destination:
            output.write('\tjmp _bf_block{}\n'.format(destination))
    else:
        output.write('\tcmp byte [rbx + r12], 0\n')
        jmp_zero = instr.get_argument()[0]
        jmp_not_zero = instr.get_argument()[1]
        if block.get_id() + 1 == jmp_zero:
            output.write('\tjne _bf_block{}\n'.format(jmp_not_zero))
        elif block.get_id() + 1 == jmp_not_zero:
            output.write('\tje _bf_block{}\n'.format(jmp_zero))
        else:
            output.write('\tjz _bf_block{}\n'.format(instr.get_argument()[0]))
            output.write('\tjmp _bf_block{}\n'.format(instr.get_argument()[1]))


def _x64_end(output, block: BrainfuckIRBlock, instr: BrainfuckIRInstruction):
    output.write('\tret\n')


def _x64_compile_block(output, block: BrainfuckIRBlock):
    opcodes = {
        BrainfuckIROpcode.Add: _x64_add,
        BrainfuckIROpcode.Ldc: _x64_set,
        BrainfuckIROpcode.Shift: _x64_shift,
        BrainfuckIROpcode.Write: _x64_write,
        BrainfuckIROpcode.Read: _x64_read,
        BrainfuckIROpcode.Branch: _x64_branch,
        BrainfuckIROpcode.End: _x64_end
    }
    output.write('_bf_block{}:\n'.format(block.get_id()))
    for instr in block.instructions():
        if instr.get_opcode() in opcodes:
            opcodes[instr.get_opcode()](output, block, instr)


def brainfuck_compile_x64_linux(output, ir: BrainfuckIRModule, module_name: str):
    _dump_runtime(output)
    for block in ir.blocks():
        if ir.is_entry(block.get_id()):
            output.write('_bf_entry:\n')
            output.write('\txor r12, r12\n')
        _x64_compile_block(output, block)

