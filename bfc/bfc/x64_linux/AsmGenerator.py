import enum


class AsmJumpIf(enum.Enum):
    Equals = 'je'
    NotEquals = 'jne'
    Greater = 'jg'
    GreaterOrEquals = 'jge'
    Lesser = 'jl'
    LesserOrEquals = 'jle'


class AsmRegister(enum.Enum):
    def __str__(self):
        return self.value

    def __add__(self, other):
        return f'{self.value} + {str(other)}'

    def __sub__(self, other):
        return f'{self._value} - {str(other)}'


class AsmRegister64(AsmRegister):
    RAX = 'rax'
    RBX = 'rbx'
    RCX = 'rcx'
    RDX = 'rdx'
    RSP = 'rsp'
    RBP = 'rbp'
    RSI = 'rsi'
    RDI = 'rdi'
    R8 = 'r8'
    R9 = 'r9'
    R10 = 'r10'
    R11 = 'r11'
    R12 = 'r12'
    R13 = 'r13'
    R14 = 'r14'
    R15 = 'r15'


class AsmRegister32(AsmRegister):
    EAX = 'eax'
    EBX = 'ebx'
    ECX = 'ecx'
    EDX = 'edx'
    ESP = 'esp'
    EBP = 'ebp'
    ESI = 'esi'
    EDI = 'edi'


class AsmRegister16(AsmRegister):
    AX = 'ax'
    BX = 'bx'
    CX = 'cx'
    DX = 'dx'
    SP = 'sp'
    BP = 'bp'
    SI = 'si'
    DI = 'di'


class AsmRegister8(AsmRegister):
    AL = 'al'
    AH = 'ah'
    BL = 'bl'
    BH = 'bh'
    CL = 'cl'
    CH = 'ch'
    DL = 'dl'
    DH = 'dh'


class AsmPointerType(enum.Enum):
    Byte = 'byte'
    Word = 'word'
    DWord = 'dword'
    QWord = 'qword'

    def __str__(self):
        return self.value


class AsmAbstractRegister(enum.Enum):
    RegA = 'a'
    RegB = 'b'
    RegC = 'c'
    RegD = 'd'

    def get_reg(self, pointer_type: AsmPointerType):
        if pointer_type == AsmPointerType.Byte:
            return f'{self.value}l'
        elif pointer_type == AsmPointerType.Word:
            return f'{self.value}x'
        elif pointer_type == AsmPointerType.DWord:
            return f'e{self.value}x'
        elif pointer_type == AsmPointerType.QWord:
            return f'r{self.value}x'


class AsmLabel:
    def __init__(self, output, label: str):
        self._output = output
        self._label = label

    def get_label(self)->str:
        return self._label

    def jump(self):
        self._output.write(f'\tjmp {self._label}\n')

    def jump_if(self, condition: AsmJumpIf):
        self._output.write(f'\t{condition.value} {self._label}\n')

    def put(self):
        self._output.write(f'{self._label}:\n')

    def __str__(self):
        return self._label


class AsmGenerator:
    def __init__(self, output):
        self._output = output

    def define(self, name: str, value):
        self._output.write(f'%define {name} {value}\n')

    def label(self, label: str)->AsmLabel:
        return AsmLabel(self._output, label)

    def pointer(self, pointer_type: AsmPointerType, to):
        return f'{str(pointer_type)} [{to}]'

    def mov(self, dest, src):
        self._output.write(f'\tmov {str(dest)}, {str(src)}\n')

    def add(self, dest, src):
        self._output.write(f'\tadd {str(dest)}, {str(src)}\n')

    def sub(self, dest, src):
        self._output.write(f'\tsub {str(dest)}, {str(src)}\n')

    def xor(self, dest, src):
        self._output.write(f'\txor {str(dest)}, {str(src)}\n')

    def cmp(self, dest, src):
        self._output.write(f'\tcmp {str(dest)}, {str(src)}\n')

    def push(self, src):
        self._output.write(f'\tpush {str(src)}\n')

    def pop(self, dst):
        self._output.write(f'\tpop {str(dst)}\n')

    def imul(self, multiply):
        self._output.write(f'\timul {str(multiply)}\n')

    def call(self, proc: str):
        self._output.write(f'\tcall {proc}\n')

    def ret(self):
        self._output.write('\tret\n')

    def dump(self, file):
        self._output.write(file.read())
        self._output.write('\n')