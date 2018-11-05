import enum
import io


class BrainfuckIROpcode(enum.Enum):
    Add = 'Add'
    Ldc = 'Ldc'
    Shift = 'Shift'
    Write = 'Write'
    Read = 'Read'
    Branch = 'Branch'
    End = 'End'


class BrainfuckIRInstruction:
    def __init__(self, opcode: BrainfuckIROpcode, argument = None):
        self._opcode = opcode
        self._argument = argument

    def get_opcode(self)->BrainfuckIROpcode:
        return self._opcode

    def get_argument(self):
        return self._argument

    def __str__(self):
        if self._argument is not None:
            return '{} {}'.format(self._opcode.value, self._argument)
        else:
            return self._opcode.value


class BrainfuckIRBlock:
    def __init__(self, block_id: int):
        self._block_id = block_id
        self._code = list()

    def get_id(self)->int:
        return self._block_id

    def add(self, value: int):
        if value != 0:
            self._code.append(BrainfuckIRInstruction(BrainfuckIROpcode.Add, value))

    def load(self, value: int):
        self._code.append(BrainfuckIRInstruction(BrainfuckIROpcode.Ldc, value))

    def shift(self, value: int):
        if value != 0:
            self._code.append(BrainfuckIRInstruction(BrainfuckIROpcode.Shift, value))

    def write(self):
        self._code.append(BrainfuckIRInstruction(BrainfuckIROpcode.Write))

    def read(self):
        self._code.append(BrainfuckIRInstruction(BrainfuckIROpcode.Read))

    def branch(self, bz: int, bnz: int):
        self._code.append(BrainfuckIRInstruction(BrainfuckIROpcode.Branch, (bz, bnz)))

    def finalize(self):
        if len(self._code) == 0 or self._code[-1].get_opcode() != BrainfuckIROpcode.Branch:
            self._code.append(BrainfuckIRInstruction(BrainfuckIROpcode.End))

    def instructions(self):
        return self._code

    def __str__(self):
        out = io.StringIO()
        out.write('{}:\n'.format(self._block_id))
        for instr in self._code:
            out.write('\t{}\n'.format(str(instr)))
        return out.getvalue().strip()


class BrainfuckIRModule:
    def __init__(self):
        self._entry = None
        self._blocks = list()

    def new_block(self)->BrainfuckIRBlock:
        block = BrainfuckIRBlock(len(self._blocks))
        self._blocks.append(block)
        return block

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
