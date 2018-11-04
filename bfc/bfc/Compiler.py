from bfc.AST import *


def brainfuck_compile(ast, codegen, loop = None):
    for node in ast.get_body():
        if node.get_type() == BrainfuckNodeType.Operation:
            if node.get_operation() == BrainfuckASTOperation.Add:
                codegen.add(node.get_argument())
            elif node.get_operation() == BrainfuckASTOperation.Shift:
                codegen.shift(node.get_argument())
            elif node.get_operation() == BrainfuckASTOperation.Write:
                codegen.write()
            elif node.get_operation() == BrainfuckASTOperation.Read:
                codegen.read()
            elif node.get_operation() == BrainfuckASTOperation.Set:
                codegen.set(node.get_argument())
        elif node.get_type() == BrainfuckNodeType.Loop:
            brainfuck_compile(node, codegen, codegen.loop())
    if loop:
        loop()
    else:
        codegen.finalize()
