import os
from bfc.IR import *
from bfc.Options import *


class BrainfuckLinuxX64:
    CELL_SIZE_ALIAS = {
        MemoryCellSize.Byte: 'byte',
        MemoryCellSize.Word: 'word',
        MemoryCellSize.DWord: 'dword',
    }

    def __init__(self, options: BrainfuckOptions, runtime: str):
        self._next_loop_id = 0
        self._options = options
        self._runtime = runtime
        self.opcodes = {
            IROpcode.Add: self._opcode_add,
            IROpcode.Set: self._opcode_set,
            IROpcode.Shift: self._opcode_shift,
            IROpcode.Write: self._opcode_write,
            IROpcode.Read: self._opcode_read,
            IROpcode.Loop: self._opcode_loop,
            IROpcode.Copy: self._opcode_copy
        }

    def compile(self, output, module: IRInstructionBlock):
        self._next_loop_id = 0
        cell_byte_size = self._options.get_cell_size().get_size()
        output.write('%define BF_CELL_SIZE {}\n'.format(cell_byte_size))
        self._dump_runtime(output)
        output.write('_bf_entry:\n')
        output.write('\txor r12, r12\n')
        for instr in module.get_body():
            self._compile_instruction(output, instr)
        output.write('\tmov rax, 0\n')
        output.write('\tret\n')

    def _dump_runtime(self, output):
        with open(os.path.join(os.path.dirname(__file__), self._runtime)) as runtime:
            output.write(runtime.read())
            output.write('\n')

    def _compile_instruction(self, output, instr: IRInstruction):
        for dep in instr.get_dependencies():
            self._compile_instruction(output, dep)
        if instr.get_opcode() in self.opcodes:
            self.opcodes[instr.get_opcode()](output, instr)

    def _cell_pointer(self):
        if self._options.get_memory_overflow() != MemoryOverflow.Undefined:
            return 'rbx + r12'
        else:
            return 'rbx'

    def _cell(self, offset: int = 0):
        cell_size = BrainfuckLinuxX64.CELL_SIZE_ALIAS[self._options.get_cell_size()]
        cell_byte_size = self._options.get_cell_size().get_size()
        if offset != 0:
            return f'{cell_size} [{self._cell_pointer()} + {offset * cell_byte_size}]'
        else:
            return f'{cell_size} [{self._cell_pointer()}]'

    def _shift_pointer(self, output, offset: int):
        if offset != 0:
            cell_byte_size = self._options.get_cell_size().get_size()
            byte_offset = offset * cell_byte_size
            if self._options.get_memory_overflow() != MemoryOverflow.Undefined:
                output.write('\tadd r12, {}\n'.format(byte_offset))
                self._normalize_pointer(output)
            else:
                output.write('\tadd rbx, {}\n'.format(byte_offset))

    def _normalize_pointer(self, output):
        if self._options.get_memory_overflow() == MemoryOverflow.Wrap:
            output.write('\tcall _bf_normalize_pointer\n')
        elif self._options.get_memory_overflow() == MemoryOverflow.Abort:
            output.write('\tcall _bf_check_pointer\n')

    def _register(self, reg: str = 'a'):
        if self._options.get_cell_size() == MemoryCellSize.Byte:
            return f'{reg}l'
        elif self._options.get_cell_size() == MemoryCellSize.Word:
            return f'{reg}x'
        elif self._options.get_cell_size() == MemoryCellSize.DWord:
            return f'r{reg}x'

    def _opcode_add(self, output, instr: IRInstruction):
        value = instr.get_arguments()[0]
        offset = instr.get_pointer()
        command = 'add' if value > 0 else 'sub'
        absolute_value = abs(value)
        output.write(f'\t{command} {self._cell(offset)}, {absolute_value}\n')

    def _opcode_set(self, output, instr: IRInstruction):
        value = instr.get_arguments()[0]
        offset = instr.get_pointer()
        output.write(f'\tmov {self._cell(offset)}, {value}\n')

    def _opcode_shift(self, output, instr: IRInstruction):
        offset = instr.get_arguments()[0]
        self._shift_pointer(output, offset)

    def _opcode_write(self, output, instr: IRInstruction):
        offset = instr.get_pointer()
        self._shift_pointer(output, offset)
        output.write('\tcall _bf_write\n')
        self._shift_pointer(output, -offset)

    def _opcode_read(self, output, instr: IRInstruction):
        offset = instr.get_pointer()
        self._shift_pointer(output, offset)
        output.write('\tcall _bf_read\n')
        self._shift_pointer(output, -offset)

    def _opcode_copy(self, output, instr: IRInstruction):
        offsets = instr.get_arguments()
        loop_id = self._next_loop_id
        self._next_loop_id += 1
        end_label = f'_bf_copy{loop_id}_end'
        reg = self._register('a')
        output.write(f'\tmov {reg}, {self._cell()}\n')
        output.write(f'\tcmp {reg}, 0\n')
        output.write(f'\tje {end_label}\n')
        output.write(f'\tmov {self._cell()}, 0\n')
        for offset in offsets:
            self._shift_pointer(output, offset)
            output.write(f'\tadd {self._cell()}, {reg}\n')
            self._shift_pointer(output, -offset)
        output.write(f'{end_label}:\n')

    def _opcode_loop(self, output, ir: IRInstruction):
        loop_id = self._next_loop_id
        self._next_loop_id += 1
        start_label = f'_bf_loop{loop_id}_start'
        end_label = f'_bf_loop{loop_id}_end'
        output.write('\tcmp {}, 0\n'.format(self._cell()))
        output.write('\tje {}\n'.format(end_label))
        output.write('{}:\n'.format(start_label))
        for instr in ir.get_arguments()[0].get_body():
            self._compile_instruction(output, instr)
        output.write('\tcmp {}, 0\n'.format(self._cell()))
        output.write('\tjne {}\n'.format(start_label))
        output.write('{}:\n'.format(end_label))


def brainfuck_compile_x64_linux(output, module: IRInstructionBlock, options: BrainfuckOptions):
    cmp = BrainfuckLinuxX64(options, 'runtime.asm')
    cmp.compile(output, module)


def brainfuck_compile_x64_linux_lib(output, module: IRInstructionBlock, options: BrainfuckOptions):
    output.write('%define MODULE_ENTRY _bf_{}\n'.format(options.get_module_name()))
    cmp = BrainfuckLinuxX64(options, 'runtime_lib.asm')
    cmp.compile(output, module)

