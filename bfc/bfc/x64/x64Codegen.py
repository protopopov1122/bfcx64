import os


class x64Codegen:
    def __init__(self, output):
        self._output = output
        self._loopid = 0
        self._dump_runtime()
        self._output.write('_bf_entry:\n')
        self._output.write('\tmov rbx, rdi\n')
        self._output.write('\txor r12, r12\n')

    def add(self, value: int):
        if value == 1:
            self._output.write('\tinc byte [rbx + r12]\n')
        elif value == -1:
            self._output.write('\tdec byte [rbx + r12]\n')
        else:
            self._output.write('\tadd byte [rbx + r12], {}\n'.format(value))

    def set(self, value: int):
        self._output.write('\tmov byte [rbx + r12], {}\n'.format(value))

    def shift(self, value: int):
        if value == 1:
            self._output.write('\tinc r12\n')
        elif value == -1:
            self._output.write('\tdec r12\n')
        else:
            self._output.write('\tadd r12, {}\n'.format(value))
        self._output.write('\tcall _bf_normalize_pointer\n')

    def write(self):
        self._output.write('\tmov rdi, [rbx + r12]\n')
        self._output.write('\tcall _bf_write\n')

    def read(self):
        self._output.write('\tcall _bf_read\n')
        self._output.write('\tmov byte [r12 + rbx], al\n')

    def loop(self):
        label = '_bf_loop{}'.format(self._loopid)
        self._loopid += 1
        self._output.write('\tjmp {}_end\n'.format(label))
        self._output.write('{}_start:\n'.format(label))
        def close_loop():
            self._output.write('{}_end:\n'.format(label))
            self._output.write('\tcmp byte [r12 + rbx], 0\n')
            self._output.write('\tjne {}_start\n'.format(label))
        return close_loop

    def finalize(self):
        self._output.write('\tret\n')

    def _dump_runtime(self):
        with open(os.path.join(os.path.dirname(__file__), 'runtime.asm')) as runtime:
            self._output.write(runtime.read())
            self._output.write('\n')
