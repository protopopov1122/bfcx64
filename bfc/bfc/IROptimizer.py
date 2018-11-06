from bfc.IR import *


def brainfuck_ir_optimize_block(block: BrainfuckIRBlock, ir: BrainfuckIRModule):
    new_block = BrainfuckIRBlock(block.get_id())
    processed = set()
    io = list()
    terminating = list()
    free = list()
    for index, instr in enumerate(block.instructions()):
        if BrainfuckIROpcode.is_io(instr.get_opcode()):
            io.append(index)
        elif BrainfuckIROpcode.is_terminating(instr.get_opcode()):
            terminating.append(index)
        elif not instr.is_dependency() and BrainfuckIROpcode.is_modifying(instr.get_opcode()):
            free.append(index)
    def append_instr(index):
        if index is None:
            return
        if index not in processed:
            instr: BrainfuckIRInstruction = block.instructions()[index]
            append_instr(instr.get_dependency())
            if instr.get_memory_offset() != new_block.get_current_memory_offset():
                new_block.shift(instr.get_memory_offset() - new_block.get_current_memory_offset())
            new_block.add_instruction(instr.get_opcode(), instr.get_argument())
            processed.add(index)
    for instr in io: append_instr(instr)
    for instr in free: append_instr(instr)
    for instr in terminating: append_instr(instr)
    ir.replace_block(new_block)


def brainfuck_ir_optimize(ir: BrainfuckIRModule):
    for block in ir.blocks():
        brainfuck_ir_optimize_block(block, ir)