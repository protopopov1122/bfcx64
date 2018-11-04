## Brainfuck x64 compiler
This repo includes basic Brainfuck language compiler. It's implemented using Python 3 language.
It produces x64 NASM assembly code for Linux that has no external dependencies (uses only Linux syscalls).
Resulting code has few basic optimizations, but overall it's quite straightforward.

TODOs:
* Perform more tests to prove that resulting code is correct (currently I made only few tests - hello world and introspection program)
* Implement IR language that will allow advanced optimizations
* Change code generation engine to use the IR
* Add support for multiple targets


### Building
Project is written in Python 3 and has no external dependencies. Usage example:
```bash
python bfc/main.py examples/hello_world.bf
nasm -f elf64 examples/hello_world.bf.asm
ld -o hello_world examples/hello_world.bf.o
```

### Motivation
It's a one-evening project. I've got bored and implemented this compiler in a couple of hours. I'm planning to develop it further. Just for fun.

### Author
Jevgenijs Protopopovs

