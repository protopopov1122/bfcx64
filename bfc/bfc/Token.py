import enum
import io


class BrainfuckToken(enum.Enum):
    PLUS = '+'
    MINUS = '-'
    RIGHT = '>'
    LEFT = '<'
    OPEN = '['
    CLOSE = ']'
    WRITE = '.'
    READ = ','

    @staticmethod
    def is_token(symbol):
        return any(symbol == token.value for token in BrainfuckToken)


def next_brainfuck_token(input)->str:
    token = None
    symbol = input.read(1)
    while symbol and token is None:
        if BrainfuckToken.is_token(symbol):
            token = BrainfuckToken(symbol)
        else:
            symbol = input.read(1)
    return token


def brainfuck_tokenize(input: io.StringIO)->str:
    token = next_brainfuck_token(input)
    while token:
        yield token
        token = next_brainfuck_token(input)
