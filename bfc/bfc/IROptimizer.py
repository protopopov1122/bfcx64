from bfc.IR import *
import abc


def match_opcode(opcode: IROpcode):
    def proc(block: [IRInstruction]):
        return [block[-1]] if len(block) > 0 and block[-1].get_opcode() == opcode else None
    return proc


def match_instruction(opcode: IROpcode, *args):
    def proc(block: [IRInstruction]):
        if len(block) == 0 or block[-1].get_opcode() != opcode:
            return None
        instr = block[-1]
        if len(instr.get_arguments()) < len(args):
            return None
        for index, matcher in enumerate(args):
            if not matcher(instr.get_arguments()[index]):
                return None
        return [block[-1]]
    return proc


def match_integer(value: int):
    def proc(actual_value: int):
        return actual_value == value
    return proc


def match_multiple(matcher, min: int = 1, max: int = None):
    def proc(block: [IRInstruction]):
        matched = 0
        offset = 0
        while offset <= len(block):
            match = matcher(block[:len(block) - offset])
            if match is not None:
                matched += 1
                offset += len(match)
            else:
                break
        return block[len(block) - offset:] if matched >= min and (max is None or matched <= max) else None
    return proc


def match_sequence(*args, whole_sequence: bool = False):
    def proc(block: [IRInstruction]):
        offset = 0
        for matcher in reversed(args):
            match = matcher(block[:len(block) - offset])
            if match:
                offset += len(match)
            else:
                return None
        return block[len(block) - offset:] if not whole_sequence or offset == len(block) else None
    return proc


def match_or(*args):
    def proc(value):
        for matcher in args:
            match = matcher(value)
            if matcher(value):
                return match
        return None
    return proc


def match_loop(matcher = None, is_determined: bool = False):
    def proc(block: [IRInstruction]):
        if len(block) == 0 or block[-1].get_opcode() != IROpcode.Loop:
            return None
        else:
            return [block[-1]] if (matcher is None or matcher(block[-1].get_arguments()[0].get_body())) and \
                                  (not is_determined or block[-1].get_arguments()[0].get_memory_space() is not None) else None
    return proc


def optimize_merge_add(block: [IRInstruction], match):
    instr1 = block[-2]
    instr2 = block[-1]
    add_instr = IRInstructionBuilder.add(instr1.get_arguments()[0] + instr2.get_arguments()[0])
    del block[-1]
    del block[-1]
    block.append(add_instr)


def optimize_merge_shift(block: [IRInstruction], match):
    instr1 = block[-2]
    instr2 = block[-1]
    shift_instr = IRInstructionBuilder.shift(instr1.get_arguments()[0] + instr2.get_arguments()[0])
    del block[-1]
    del block[-1]
    block.append(shift_instr)


def optimize_merge_add_set(block: [IRInstruction], match):
    instr1 = block[-2]
    instr2 = block[-1]
    set_instr = IRInstructionBuilder.set(instr1.get_arguments()[0] + instr2.get_arguments()[0])
    del block[-1]
    del block[-1]
    block.append(set_instr)


def optimize_merge_set(block: [IRInstruction], match):
    del block[-2]


def optimize_zero_set(block: [IRInstruction], match):
    del block[-1]
    block.append(IRInstructionBuilder.set(0))


def optimize_loop(block: [IRInstruction], match):
    loop_body = block[-1].get_arguments()[0].get_body()
    loop = IRInstructionBuilder.loop(IRInstructionBlock(brainfuck_optimize_block(loop_body)))
    del block[-1]
    block.append(loop)


def optimize_copy(block: [IRInstruction], match):
    copies = list()
    offset = 0
    slice = block[-1].get_arguments()[0].get_body()[1:]
    while len(slice) > 2 and slice[0].get_opcode() == IROpcode.Shift:
        offset += slice[0].get_arguments()[0]
        multiply = slice[1].get_arguments()[0]
        copies.append((offset, multiply))
        slice = slice[2:]
    del block[-1]
    block.append(IRInstructionBuilder.copy(copies))


def brainfuck_optimize_block(block: [IRInstruction]):
    transform = [
        (match_sequence(match_opcode(IROpcode.Add), match_opcode(IROpcode.Add)), optimize_merge_add),
        (match_sequence(match_opcode(IROpcode.Set), match_opcode(IROpcode.Add)), optimize_merge_add_set),
        (match_sequence(match_opcode(IROpcode.Set), match_opcode(IROpcode.Set)), optimize_merge_set),
        (match_sequence(match_opcode(IROpcode.Shift), match_opcode(IROpcode.Shift)), optimize_merge_shift),
        (match_loop(
            match_sequence(
                match_instruction(IROpcode.Add,
                                      match_or(
                                          match_integer(1),
                                          match_integer(-1)
                                      )
                                  ), whole_sequence=True
            )
        ), optimize_zero_set),
        (match_loop(), optimize_loop),
        (
            match_loop(
                match_sequence(
                    match_instruction(IROpcode.Add, match_integer(-1)),
                    match_multiple(match_sequence(
                      match_opcode(IROpcode.Shift),
                      match_opcode(IROpcode.Add)
                    )),
                    match_opcode(IROpcode.Shift),
                    whole_sequence=True
                ), is_determined=True
            ), optimize_copy
        )
    ]
    new_block = list()
    for instr in block:
        new_block.append(instr)
        for matcher, transformation in transform:
            match = matcher(new_block)
            if match is not None:
                transformation(new_block, match)
    return new_block


def brainfuck_ir_optimize(module: IRInstructionBlock):
    return IRInstructionBlock(brainfuck_optimize_block(module.get_body()))
