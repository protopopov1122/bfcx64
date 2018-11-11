from bfc.x64.x64Codegen import brainfuck_compile_x64


Codegen = {
    'x64': brainfuck_compile_x64,
    'raw': lambda output, module: output.write(str(module))
}
