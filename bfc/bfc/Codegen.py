from bfc.x64_linux.Codegen import brainfuck_compile_x64_linux
from bfc.x64_linux_compat.Codegen import brainfuck_compile_x64_linux_compat


Codegen = {
    'x64-linux': brainfuck_compile_x64_linux,
    'x64-linux-compat': brainfuck_compile_x64_linux_compat,
    'raw': lambda output, module, module_name: output.write(str(module))
}
