import enum


class MemoryOverflow(enum.Enum):
    Undefined = 'undefined'
    Wrap = 'Wrap'


class MemoryCellSize(enum.Enum):
    Byte = 1
    Word = 2
    DWord = 4

    def get_size(self)->int:
        return self.value


class BrainfuckOptions:
    def __init__(self, module_name: str, memory_overflow: MemoryOverflow = MemoryOverflow.Undefined, cell_size: MemoryCellSize = MemoryCellSize.Byte):
        self._module_name = module_name
        self._memory_overflow = memory_overflow
        self._cell_size = cell_size

    def get_module_name(self)->str:
        return self._module_name

    def get_memory_overflow(self)->MemoryOverflow:
        return self._memory_overflow

    def get_cell_size(self)->MemoryCellSize:
        return self._cell_size
