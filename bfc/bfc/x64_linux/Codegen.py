import os
from bfc.IR import *
from bfc.Options import *
from bfc.x64_linux.AsmGenerator import *


class BrainfuckLinuxX64:
    CELL_SIZE_ALIAS = {
        MemoryCellSize.Byte: AsmPointerType.Byte,
        MemoryCellSize.Word: AsmPointerType.Word,
        MemoryCellSize.DWord: AsmPointerType.DWord
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
        gen = AsmGenerator(output)
        self._next_loop_id = 0
        cell_byte_size = self._options.get_cell_size().get_size()
        gen.define('BF_CELL_SIZE', cell_byte_size)
        gen.define('BF_ABORT_ON_OVERFLOW', 1 if self._options.get_memory_overflow() == MemoryOverflow.Abort else 0)
        gen.define('BF_WRAP_ON_OVERFLOW', 1 if self._options.get_memory_overflow() == MemoryOverflow.Wrap else 0)
        self._dump_runtime(gen)
        gen.label('_bf_entry').put()
        gen.xor(AsmRegister64.R12, AsmRegister64.R12)
        for instr in module.get_body():
            self._compile_instruction(gen, instr)
        gen.mov(AsmRegister64.RAX, 0)
        gen.ret()

    def _dump_runtime(self, gen):
        with open(os.path.join(os.path.dirname(__file__), self._runtime)) as runtime:
            gen.dump(runtime)

    def _compile_instruction(self, gen, instr: IRInstruction):
        for dep in instr.get_dependencies():
            self._compile_instruction(gen, dep)
        if instr.get_opcode() in self.opcodes:
            self.opcodes[instr.get_opcode()](gen, instr)

    def _cell_pointer(self):
        if self._options.get_memory_overflow() != MemoryOverflow.Undefined:
            return AsmRegister64.RBX + AsmRegister64.R12
        else:
            return AsmRegister64.RBX

    def _cell(self, gen: AsmGenerator, offset: int = 0):
        cell_size = BrainfuckLinuxX64.CELL_SIZE_ALIAS[self._options.get_cell_size()]
        cell_byte_size = self._options.get_cell_size().get_size()
        if offset != 0:
            return gen.pointer(cell_size, f'{self._cell_pointer()} + {offset * cell_byte_size}')
        else:
            return gen.pointer(cell_size, self._cell_pointer())

    def _shift_pointer(self, gen: AsmGenerator, offset: int):
        if offset != 0:
            cell_byte_size = self._options.get_cell_size().get_size()
            command = gen.add if offset > 0 else gen.sub
            byte_offset = abs(offset * cell_byte_size)
            if self._options.get_memory_overflow() != MemoryOverflow.Undefined:
                command(AsmRegister64.R12, byte_offset)
                self._normalize_pointer(gen)
            else:
                command(AsmRegister64.RBX, byte_offset)

    def _normalize_pointer(self, gen):
        if self._options.get_memory_overflow() == MemoryOverflow.Wrap:
            gen.call('_bf_normalize_pointer')
        elif self._options.get_memory_overflow() == MemoryOverflow.Abort:
            gen.call('_bf_check_pointer')

    def _register(self, reg: str = 'a'):
        if self._options.get_cell_size() == MemoryCellSize.Byte:
            return f'{reg}l'
        elif self._options.get_cell_size() == MemoryCellSize.Word:
            return f'{reg}x'
        elif self._options.get_cell_size() == MemoryCellSize.DWord:
            return f'e{reg}x'

    def _opcode_add(self, gen, instr: IRInstruction):
        value = instr.get_arguments()[0]
        offset = instr.get_pointer()
        command = gen.add if value > 0 else gen.sub
        absolute_value = abs(value)
        command(self._cell(gen, offset), absolute_value)

    def _opcode_set(self, gen, instr: IRInstruction):
        value = instr.get_arguments()[0]
        offset = instr.get_pointer()
        gen.mov(self._cell(gen, offset), value)

    def _opcode_shift(self, gen, instr: IRInstruction):
        offset = instr.get_arguments()[0]
        self._shift_pointer(gen, offset)

    def _opcode_write(self, gen, instr: IRInstruction):
        offset = instr.get_pointer()
        self._shift_pointer(gen, offset)
        gen.call('_bf_write')
        self._shift_pointer(gen, -offset)

    def _opcode_read(self, gen, instr: IRInstruction):
        offset = instr.get_pointer()
        self._shift_pointer(gen, offset)
        gen.call('_bf_read')
        self._shift_pointer(gen, -offset)

    def _opcode_copy(self, gen: AsmGenerator, instr: IRInstruction):
        cell_size = BrainfuckLinuxX64.CELL_SIZE_ALIAS[self._options.get_cell_size()]
        offsets = instr.get_arguments()
        loop_id = self._next_loop_id
        self._next_loop_id += 1
        end_label = gen.label(f'_bf_copy{loop_id}_end')
        reg = AsmAbstractRegister.RegC.get_reg(cell_size)
        mulreg = AsmAbstractRegister.RegA.get_reg(cell_size)
        gen.mov(reg, self._cell(gen))
        gen.cmp(reg, 0)
        end_label.jump_if(AsmJumpIf.Equals)
        gen.mov(self._cell(gen), 0)
        pointer = 0
        direct_pointing = self._options.get_memory_overflow() == MemoryOverflow.Undefined
        for offset, multiply in offsets:
            if multiply == 1:
                srcreg = reg
            else:
                gen.push(multiply)
                gen.mov(mulreg, reg)
                gen.imul(gen.pointer(cell_size, AsmRegister64.RSP))
                gen.pop(AsmRegister64.RDI)
                srcreg = mulreg
            if direct_pointing:
                gen.add(self._cell(gen, offset), srcreg)
            else:
                self._shift_pointer(gen, offset - pointer)
                pointer = offset
                gen.add(self._cell(gen), srcreg)
        if pointer != 0:
            self._shift_pointer(gen, -pointer)
        end_label.put()

    def _opcode_loop(self, gen: AsmGenerator, ir: IRInstruction):
        loop_id = self._next_loop_id
        self._next_loop_id += 1
        start_label = gen.label(f'_bf_loop{loop_id}_start')
        end_label = gen.label(f'_bf_loop{loop_id}_end')
        gen.cmp(self._cell(gen), 0)
        end_label.jump_if(AsmJumpIf.Equals)
        start_label.put()
        for instr in ir.get_arguments()[0].get_body():
            self._compile_instruction(gen, instr)
        gen.cmp(self._cell(gen), 0)
        start_label.jump_if(AsmJumpIf.NotEquals)
        end_label.put()


def brainfuck_compile_x64_linux(output, module: IRInstructionBlock, options: BrainfuckOptions):
    cmp = BrainfuckLinuxX64(options, 'runtime.asm')
    cmp.compile(output, module)


def brainfuck_compile_x64_linux_lib(output, module: IRInstructionBlock, options: BrainfuckOptions):
    output.write('%define MODULE_ENTRY _bf_{}\n'.format(options.get_module_name()))
    cmp = BrainfuckLinuxX64(options, 'runtime_lib.asm')
    cmp.compile(output, module)

