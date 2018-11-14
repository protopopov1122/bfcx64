import enum


class IROpcode(enum.Enum):
    Add = 'Add'
    Shift = 'Shift'
    Write = 'Write'
    Read = 'Read'
    Loop = 'Loop'
    Set = 'Set'
    Nop = 'Nop'
    Copy = 'Copy'

    def requires_explicit_shift(self)->bool:
        return self in [IROpcode.Loop, IROpcode.Copy, IROpcode.Read, IROpcode.Write, IROpcode.Nop]



class IRInstruction:
    def __init__(self, opcode: IROpcode, *args):
        self._opcode = opcode
        self._args = args
        self._pointer = 0
        self._dependencies = list()

    def get_opcode(self)->IROpcode:
        return self._opcode

    def get_arguments(self):
        return self._args

    def get_pointer(self)->int:
        return self._pointer

    def set_pointer(self, pointer: int):
        self._pointer = pointer

    def get_dependencies(self)->list:
        return self._dependencies

    def add_dependency(self, instr):
        self._dependencies.append(instr)

    def __str__(self):
        if self._opcode != IROpcode.Loop:
            return '{} {} {}'.format(self._opcode, self._args, self._pointer)
        else:
            return 'loop [{}] {}'.format('; '.join([str(instr) for instr in self._args[0].get_body()]), self._pointer)


class IRInstructionBlock:
    def __init__(self, body: [IRInstruction]):
        self._body = body

    def get_body(self)->[IRInstruction]:
        return self._body

    def get_memory_space(self):
        offset = 0
        minimal_offset = 0
        maximal_offset = 0
        for instr in self._body:
            if instr.get_opcode() == IROpcode.Shift:
                offset += instr.get_arguments()[0]
                if offset > maximal_offset:
                    maximal_offset = offset
                elif offset < minimal_offset:
                    minimal_offset = offset
            elif instr.get_opcode() == IROpcode.Loop:
                loop_mem = instr.get_arguments()[0].get_memory_space()
                if loop_mem is None:
                    return None
                if offset + loop_mem[1] > maximal_offset:
                    maximal_offset = offset + loop_mem[1]
                if offset + loop_mem[0] < minimal_offset:
                    minimal_offset = offset + loop_mem[0]
        if offset == 0:
            return minimal_offset, maximal_offset
        else:
            return None


class IRInstructionBuilder:
    @staticmethod
    def add(value: int):
        return IRInstruction(IROpcode.Add, value)

    @staticmethod
    def set(value: int):
        return IRInstruction(IROpcode.Set, value)

    @staticmethod
    def shift(value: int):
        return IRInstruction(IROpcode.Shift, value)

    @staticmethod
    def write():
        return IRInstruction(IROpcode.Write)

    @staticmethod
    def read():
        return IRInstruction(IROpcode.Read)

    @staticmethod
    def loop(block: IRInstructionBlock):
        return IRInstruction(IROpcode.Loop, block)

    @staticmethod
    def nop():
        return IRInstruction(IROpcode.Nop)

    @staticmethod
    def copy(offsets: [int]):
        return IRInstruction(IROpcode.Copy, *offsets)