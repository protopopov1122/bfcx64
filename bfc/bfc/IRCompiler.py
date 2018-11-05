from bfc.AST import *
from bfc.IR import *


def brainfuck_compile_ir_block(ast: BrainfuckASTBlock, ir: BrainfuckIRModule, block: BrainfuckIRBlock):
    for node in ast.get_body():
        if node.get_type() == BrainfuckNodeType.Operation:
            if node.get_operation() == BrainfuckASTOperation.Add:
                block.add(node.get_argument())
            elif node.get_operation() == BrainfuckASTOperation.Set:
                block.load(node.get_argument())
            elif node.get_operation() == BrainfuckASTOperation.Shift:
                block.shift(node.get_argument())
            elif node.get_operation() == BrainfuckASTOperation.Write:
                block.write()
            elif node.get_operation() == BrainfuckASTOperation.Read:
                block.read()
        elif node.get_type() == BrainfuckNodeType.Loop:
            loop_block = ir.new_block()
            loop_end_block = brainfuck_compile_ir_block(node.get_block(), ir, loop_block)
            next_block = ir.new_block()
            block.branch(next_block.get_id(), loop_block.get_id())
            loop_end_block.branch(next_block.get_id(), loop_block.get_id())
            block = next_block
    return block



def brainfuck_compile_ir(ast: BrainfuckASTBlock):
    ir = BrainfuckIRModule()
    entry = ir.new_block()
    brainfuck_compile_ir_block(ast, ir, entry)
    ir.set_entry(entry.get_id())
    ir.finalize()
    return ir