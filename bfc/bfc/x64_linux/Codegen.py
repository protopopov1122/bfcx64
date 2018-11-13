import os
from bfc.IR import *
from bfc.Options import *


class BrainfuckLinuxX64:
    def __init__(self, options: BrainfuckOptions, runtime: str):
        self._loop = 0
        self._options = options
        self._runtime = runtime
        self.opcodes = {
            IROpcode.Add: self._add_wrap,
            IROpcode.Set: self._x64_set,
            IROpcode.Shift: self._x64_shift,
            IROpcode.Write: self._x64_write,
            IROpcode.Read: self._x64_read,
            IROpcode.Loop: self._x64_loop,
        }
        self.cell_sizes = {
            MemoryCellSize.Byte: 'byte',
            MemoryCellSize.Word: 'word',
            MemoryCellSize.DWord: 'dword',
        }
        self.cell_byte_sizes = {
            MemoryCellSize.Byte: 1,
            MemoryCellSize.Word: 2,
            MemoryCellSize.DWord: 4,
        }

    def compile(self, output, module: IRInstructionBlock):
        self._loop = 0
        cell_byte_size = self.cell_byte_sizes[self._options.get_cell_size()]
        output.write('%define BF_CELL_SIZE {}\n'.format(cell_byte_size))
        self._dump_runtime(output)
        output.write('_bf_entry:\n')
        output.write('\txor r12, r12\n')
        for instr in module.get_body():
            self._x64_compile_instruction(output, instr)
        output.write('\tret\n')

    def _dump_runtime(self, output):
        with open(os.path.join(os.path.dirname(__file__), self._runtime)) as runtime:
            output.write(runtime.read())
            output.write('\n')

    def _x64_compile_instruction(self, output, instr: IRInstruction):
        if instr.get_opcode() in self.opcodes:
            self.opcodes[instr.get_opcode()](output, instr)

    def _add_wrap(self, output, instr: IRInstruction):
        value, offset = instr.get_arguments()
        command = 'add' if value > 0 else 'sub'
        absvalue = abs(value)
        cell = 'rbx + r12' if self._options.get_memory_overflow() == MemoryOverflow.Wrap else 'rbx'
        cell_size = self.cell_sizes[self._options.get_cell_size()]
        if offset == 0:
            output.write('\t{} {} [{}], {}\n'.format(command, cell_size, cell, absvalue))
        else:
            output.write('\t{} {} [{} + {}], {}\n'.format(command, cell_size, cell, offset, absvalue))

    def _x64_set(self, output, instr: IRInstruction):
        value, offset = instr.get_arguments()
        cell = 'rbx + r12' if self._options.get_memory_overflow() == MemoryOverflow.Wrap else 'rbx'
        cell_size = self.cell_sizes[self._options.get_cell_size()]
        if offset == 0:
            output.write('\tmov {} [{}], {}\n'.format(cell_size, cell, value))
        else:
            output.write('\tmov {} [{} + {}], {}\n'.format(cell_size, cell, offset, value))

    def _x64_shift(self, output, instr: IRInstruction):
        cell_byte_size = self.cell_byte_sizes[self._options.get_cell_size()]
        if self._options.get_memory_overflow() == MemoryOverflow.Wrap:
            output.write('\tadd r12, {}\n'.format(instr.get_arguments()[0] * cell_byte_size))
            self._x64_normalize_pointer(output)
        else:
            output.write('\tadd rbx, {}\n'.format(instr.get_arguments()[0] * cell_byte_size))

    def _x64_write(self, output, instr: IRInstruction):
        cell_byte_size = self.cell_byte_sizes[self._options.get_cell_size()]
        offset = instr.get_arguments()[0] * cell_byte_size
        if offset == 0:
            output.write('\tcall _bf_write\n')
        else:
            cell = 'rbx' if self._options.get_memory_overflow() == MemoryOverflow.Wrap else 'rbx'
            output.write('\tadd {}, {}\n'.format(cell, offset))
            self._x64_normalize_pointer(output)
            output.write('\tcall _bf_write\n')
            output.write('\tsub {}, {}\n'.format(cell, offset))
            self._x64_normalize_pointer(output)

    def _x64_read(self, output, instr: IRInstruction):
        cell_byte_size = self.cell_byte_sizes[self._options.get_cell_size()]
        offset = instr.get_arguments()[0] * cell_byte_size
        if offset == 0:
            output.write('\tcall _bf_read\n')
        else:
            cell = 'r12' if self._options.get_memory_overflow() == MemoryOverflow.Wrap else 'rbx'
            output.write('\tadd {}, {}\n'.format(cell, offset))
            self._x64_normalize_pointer(output)
            output.write('\tcall _bf_read\n')
            output.write('\tadd {}, {}\n'.format(cell, -offset))
            self._x64_normalize_pointer(output)

    def _x64_loop(self, output, ir: IRInstruction):
        loop_id = self._loop
        self._loop += 1
        cell = 'rbx + r12' if self._options.get_memory_overflow() == MemoryOverflow.Wrap else 'rbx'
        cell_size = self.cell_sizes[self._options.get_cell_size()]
        start_label = '_bf_loop{}_start'.format(loop_id)
        end_label = '_bf_loop{}_end'.format(loop_id)
        output.write('\tcmp {} [{}], 0\n'.format(cell_size, cell))
        output.write('\tje {}\n'.format(end_label))
        output.write('{}:\n'.format(start_label))
        for instr in ir.get_arguments()[0].get_body():
            self._x64_compile_instruction(output, instr)
        output.write('\tcmp {} [{}], 0\n'.format(cell_size, cell))
        output.write('\tjne {}\n'.format(start_label))
        output.write('{}:\n'.format(end_label))

    def _x64_normalize_pointer(self, output):
        if self._options.get_memory_overflow() == MemoryOverflow.Wrap:
            output.write('\tcall _bf_normalize_pointer\n')


def brainfuck_compile_x64_linux(output, module: IRInstructionBlock, options: BrainfuckOptions):
    cmp = BrainfuckLinuxX64(options, 'runtime.asm')
    cmp.compile(output, module)


def brainfuck_compile_x64_linux_lib(output, module: IRInstructionBlock, options: BrainfuckOptions):
    output.write('%define MODULE_ENTRY _bf_{}\n'.format(options.get_module_name()))
    cmp = BrainfuckLinuxX64(options, 'runtime_lib.asm')
    cmp.compile(output, module)

