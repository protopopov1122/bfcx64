import enum
import io


class BrainfuckIROpcode(enum.Enum):
    Add = 'Add'
    Ldc = 'Ldc'
    Shift = 'Shift'
    Write = 'Write'
    Read = 'Read'
    Branch = 'Branch'
    Nop = 'Nop'
    End = 'End'

    @staticmethod
    def is_io(opcode)->bool:
        return opcode == BrainfuckIROpcode.Write or \
            opcode == BrainfuckIROpcode.Read

    @staticmethod
    def is_terminating(opcode)->bool:
        return opcode == BrainfuckIROpcode.Branch or \
            opcode == BrainfuckIROpcode.End

    @staticmethod
    def is_modifying(opcode)->bool:
        return opcode == BrainfuckIROpcode.Add or \
            opcode == BrainfuckIROpcode.Ldc or \
            opcode == BrainfuckIROpcode.Read

class BrainfuckIRInstruction:
    def __init__(self, opcode: BrainfuckIROpcode, argument = None, mem_offset: int = None, dependency: int = None):
        self._opcode = opcode
        self._argument = argument
        self._mem_offset = mem_offset
        self._depends = dependency
        self._is_dependency = False

    def get_opcode(self)->BrainfuckIROpcode:
        return self._opcode

    def get_argument(self):
        return self._argument

    def get_memory_offset(self)->int:
        return self._mem_offset

    def get_dependency(self)->int:
        return self._depends

    def make_dependency(self):
        self._is_dependency = True

    def is_dependency(self)->bool:
        return self._is_dependency

    def __str__(self):
        res = ''
        if self._argument is not None:
            res = '{} {}'.format(self._opcode.value, self._argument)
        else:
            res = '{}'.format(self._opcode.value)
        if self._depends is not None:
            res += '\t@{}'.format(self._depends)
        return res


class BrainfuckIRBlock:
    def __init__(self, block_id: int):
        self._block_id = block_id
        self._code = list()
        self._modifiers = dict()
        self._current_offset = 0

    def get_id(self)->int:
        return self._block_id

    def get_current_memory_offset(self)->int:
        return self._current_offset

    def add(self, value: int):
        if value != 0:
            self.add_instruction(BrainfuckIROpcode.Add, value)

    def load(self, value: int):
        self.add_instruction(BrainfuckIROpcode.Ldc, value)

    def shift(self, value: int):
        if value != 0:
            self.add_instruction(BrainfuckIROpcode.Shift, value)
        self._current_offset += value

    def write(self):
        self.add_instruction(BrainfuckIROpcode.Write)

    def read(self):
        self.add_instruction(BrainfuckIROpcode.Read)

    def branch(self, bz: int, bnz: int):
        self.add_instruction(BrainfuckIROpcode.Branch, (bz, bnz))

    def jump(self, destination: int):
        self.add_instruction(BrainfuckIROpcode.Branch, destination)

    def finalize(self):
        if len(self._code) == 0 or self._code[-1].get_opcode() != BrainfuckIROpcode.Branch:
            self.add_instruction(BrainfuckIROpcode.End)

    def instructions(self):
        return self._code

    def add_instruction(self, opcode: BrainfuckIROpcode, argument = None):
        depends = None
        if self._current_offset in self._modifiers:
            depends = self._modifiers[self._current_offset]
            if BrainfuckIROpcode.is_io(opcode) or \
                BrainfuckIROpcode.is_modifying(opcode) or \
                BrainfuckIROpcode.is_terminating(opcode):
                self._code[depends].make_dependency()
        if BrainfuckIROpcode.is_modifying(opcode):
            self._modifiers[self._current_offset] = len(self._code)
        self._code.append(BrainfuckIRInstruction(opcode, argument, mem_offset=self._current_offset, dependency=depends))

    def replace_instruction(self, index: int, instr: BrainfuckIRInstruction):
        self._code[index] = instr

    def __str__(self):
        out = io.StringIO()
        out.write('{}:\n'.format(self._block_id))
        for index, instr in enumerate(self._code):
            out.write('\t#{}\t{}\n'.format(index, str(instr)))
        return out.getvalue().strip()


class BrainfuckIRModule:
    def __init__(self):
        self._entry = None
        self._blocks = list()

    def new_block(self)->BrainfuckIRBlock:
        block = BrainfuckIRBlock(len(self._blocks))
        self._blocks.append(block)
        return block

    def replace_block(self, block: BrainfuckIRBlock):
        self._blocks[block.get_id()] = block

    def set_entry(self, block_id: int):
        self._entry = block_id

    def is_entry(self, block_id: int):
        return block_id == self._entry

    def blocks(self):
        return self._blocks

    def finalize(self):
        for block in self._blocks:
            block.finalize()

    def __str__(self):
        out = io.StringIO()
        out.write('entry {}\n'.format(self._entry))
        for block in self._blocks:
            out.write('{}\n'.format(str(block)))
        return out.getvalue().strip()
