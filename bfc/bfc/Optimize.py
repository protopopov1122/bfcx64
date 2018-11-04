from bfc.AST import *


def ast_node_operation(operation: BrainfuckASTOperation, value = None):
    def proc(node):
        return node.get_type() == BrainfuckNodeType.Operation and \
            node.get_operation() == operation and \
               (value is None or node.get_argument() == value)
    return proc


def ast_nodes(*args):
    def proc(nodes):
        if len(nodes) < len(args):
            return False
        for index, check in enumerate(args):
            if not check(nodes[-1 - index]):
                return False
        return True
    return proc


def ast_loop_nodes(*args):
    def proc(node):
        if node.get_type() != BrainfuckNodeType.Loop or \
                len(node.get_body()) != len(args):
            return False
        for index, n in enumerate(node.get_body()):
            if not args[index](n):
                return False
        return True
    return proc


def ast_merge_operation_nodes(nodes):
    nodes.append(BrainfuckOperationNode(nodes[-1].get_operation(), nodes[-2].get_argument() + nodes[-1].get_argument()))
    del nodes[-2]
    del nodes[-2]


def ast_set_zero(nodes):
    del nodes[-1]
    nodes.append(BrainfuckOperationNode(BrainfuckASTOperation.Set, 0))


def brainfuck_optimize_ast(ast):
    transforms = [
        (ast_nodes(ast_node_operation(BrainfuckASTOperation.Add), ast_node_operation(BrainfuckASTOperation.Add)), ast_merge_operation_nodes),
        (ast_nodes(ast_node_operation(BrainfuckASTOperation.Shift), ast_node_operation(BrainfuckASTOperation.Shift)), ast_merge_operation_nodes),
        (ast_nodes(ast_loop_nodes(ast_node_operation(BrainfuckASTOperation.Add, 1))), ast_set_zero),
        (ast_nodes(ast_loop_nodes(ast_node_operation(BrainfuckASTOperation.Add, -1))), ast_set_zero)
    ]
    nodes = []
    for node in ast.get_body():
        if node.get_type() == BrainfuckNodeType.Loop:
            nodes.append(BrainfuckLoopNode(brainfuck_optimize_ast(node)))
        else:
            nodes.append(node)
        for pattern, transform in transforms:
            if pattern(nodes):
                transform(nodes)
    return BrainfuckASTBlock(nodes)
