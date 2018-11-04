from bfc.AST import *
from bfc.Token import BrainfuckToken
from bfc.Error import BrainfuckError


def brainfuck_parse(tokens):
    code = [[]]
    for token in tokens:
        if token == BrainfuckToken.PLUS:
            code[-1].append(BrainfuckOperationNode(BrainfuckASTOperation.Add, 1))
        elif token == BrainfuckToken.MINUS:
            code[-1].append(BrainfuckOperationNode(BrainfuckASTOperation.Add, -1))
        elif token == BrainfuckToken.RIGHT:
            code[-1].append(BrainfuckOperationNode(BrainfuckASTOperation.Shift, 1))
        elif token == BrainfuckToken.LEFT:
            code[-1].append(BrainfuckOperationNode(BrainfuckASTOperation.Shift, -1))
        elif token == BrainfuckToken.WRITE:
            code[-1].append(BrainfuckOperationNode(BrainfuckASTOperation.Write))
        elif token == BrainfuckToken.READ:
            code[-1].append(BrainfuckOperationNode(BrainfuckASTOperation.Read))
        elif token == BrainfuckToken.OPEN:
            code.append([])
        elif token == BrainfuckToken.CLOSE:
            if len(code) < 2:
                raise BrainfuckError('Brackets are not balanced')
            loop = BrainfuckLoopNode(BrainfuckASTBlock(code[-1]))
            del code[-1]
            code[-1].append(loop)
    if len(code) > 1:
        raise BrainfuckError('Brackets are not balanced')
    return BrainfuckASTBlock(code[-1])
