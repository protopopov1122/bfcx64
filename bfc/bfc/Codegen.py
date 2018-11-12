from bfc.x64_linux.Codegen import brainfuck_compile_x64_linux, brainfuck_compile_x64_linux_lib


Codegen = {
    'x64-linux': brainfuck_compile_x64_linux,
    'x64-linux-lib': brainfuck_compile_x64_linux_lib,
    'raw': lambda output, module, module_name: output.write(str(module))
}
