import abc
import enum


class BrainfuckNodeType(enum.Enum):
    Operation = 'Operation',
    Loop = 'Loop'


class BrainfuckASTOperation:
    Set = 'Set',
    Add = 'Add',
    Shift = 'Shift',
    Write = 'Write',
    Read = 'Read'


class BrainfuckNode(abc.ABC):
    def __init__(self, node_type: BrainfuckNodeType):
        self._type = node_type

    def get_type(self)->BrainfuckNodeType:
        return self._type


class BrainfuckOperationNode(BrainfuckNode):
    def __init__(self, operation: BrainfuckASTOperation, argument: int = 0):
        super().__init__(BrainfuckNodeType.Operation)
        self._operation = operation
        self._argument = argument

    def get_operation(self)->BrainfuckASTOperation:
        return self._operation

    def get_argument(self)->int:
        return self._argument


class BrainfuckASTBlock:
    def __init__(self, block: [BrainfuckNode]):
        self._block = block

    def get_body(self)->[BrainfuckNode]:
        return self._block


class BrainfuckLoopNode(BrainfuckNode):
    def __init__(self, block: BrainfuckASTBlock):
        super().__init__(BrainfuckNodeType.Loop)
        self._block = block

    def get_body(self)->[BrainfuckNode]:
        return self._block.get_body()
