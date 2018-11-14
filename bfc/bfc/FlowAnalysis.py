from bfc.IR import *
from bfc.Options import *


def brainfuck_ir_fold_block(block: [IRInstruction]):
    new_block = list()
    pointer = 0
    flow = dict()
    for instr in block:
        if instr.get_opcode() == IROpcode.Shift:
            pointer += instr.get_arguments()[0]
        elif instr.get_opcode() == IROpcode.Add:
            add_instr = IRInstructionBuilder.add(instr.get_arguments()[0])
            add_instr.set_pointer(pointer)
            if pointer in flow:
                add_instr.add_dependency(flow[pointer])
            flow[pointer] = add_instr
        elif instr.get_opcode() == IROpcode.Set:
            set_instr = IRInstructionBuilder.set(instr.get_arguments()[0])
            set_instr.set_pointer(pointer)
            flow[pointer] = set_instr
        elif instr.get_opcode() == IROpcode.Copy:
            copy = IRInstructionBuilder.copy(instr.get_arguments())
            copy.set_pointer(pointer)
            pointer = 0
            for instr_pointer in flow.keys():
                copy.add_dependency(flow[instr_pointer])
            flow = dict()
            new_block.append(copy)
        elif instr.get_opcode() == IROpcode.Write:
            write_instr = IRInstructionBuilder.write()
            write_instr.set_pointer(pointer)
            if pointer in flow:
                write_instr.add_dependency(flow[pointer])
                del flow[pointer]
            new_block.append(write_instr)
        elif instr.get_opcode() == IROpcode.Read:
            read_instr = IRInstructionBuilder.read()
            read_instr.set_pointer(pointer)
            new_block.append(read_instr)
        elif instr.get_opcode() == IROpcode.Loop:
            loop = IRInstructionBuilder.loop(IRInstructionBlock(brainfuck_ir_fold_block(instr.get_arguments()[0].get_body())))
            loop.set_pointer(pointer)
            pointer = 0
            for instr_pointer in flow.keys():
                loop.add_dependency(flow[instr_pointer])
            flow = dict()
            new_block.append(loop)
    for instr_pointer in flow.keys():
        new_block.append(flow[instr_pointer])

    instr = IRInstructionBuilder.nop()
    instr.set_pointer(pointer)
    new_block.append(instr)
    return new_block


def brainfuck_ir_unfold_block(block: [IRInstruction], explicit_offsets: bool = True):
    new_block = list()
    pointer = 0
    def unfold_instruction(instr: IRInstruction):
        nonlocal pointer
        new_instr = None
        for dep in instr.get_dependencies():
            unfold_instruction(dep)
        if instr.get_pointer() != pointer and \
                explicit_offsets or instr.get_opcode().requires_explicit_shift():
            shift_instr = IRInstructionBuilder.shift(instr.get_pointer() - pointer)
            new_block.append(shift_instr)
            pointer = instr.get_pointer()
        if instr.get_opcode() == IROpcode.Loop:
            new_instr = IRInstructionBuilder.loop(IRInstructionBlock(brainfuck_ir_unfold_block(instr.get_arguments()[0].get_body(), explicit_offsets)))
            pointer = 0
        elif instr.get_opcode() == IROpcode.Copy:
            new_instr = IRInstruction(instr.get_opcode(), *instr.get_arguments())
            pointer = 0
        elif instr.get_opcode() != IROpcode.Nop:
            new_instr = IRInstruction(instr.get_opcode(), *instr.get_arguments())
            if not explicit_offsets:
                new_instr.set_pointer(instr.get_pointer() - pointer)
        if new_instr:
            new_block.append(new_instr)
    for instr in block:
        unfold_instruction(instr)
    return new_block


def brainfuck_ir_analyze_block(block: [IRInstruction], options: BrainfuckOptions):
    return brainfuck_ir_unfold_block(brainfuck_ir_fold_block(block), options.get_memory_overflow() != MemoryOverflow.Undefined)


def brainfuck_ir_analyze_flow(module: IRInstructionBlock, options: BrainfuckOptions):
    return IRInstructionBlock(brainfuck_ir_analyze_block(module.get_body(), options))