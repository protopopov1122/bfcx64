## Brainfuck x64 compiler
This repo includes basic Brainfuck language compiler. It's implemented using Python 3 language.
It produces x64 NASM assembly code for Linux that has no external dependencies (uses only Linux syscalls).
Resulting code has few basic optimizations, but overall it's quite straightforward.

Compiler supports following targets:
* x64-linux - produces standalone 64-bit Linux assembly
* x64-linux-lib - produces 64-bit Linux assembly that respects calling convention and exports global function that can be called by C program

Compiler options:
* memory model - defines what happens after memory overflow/underflow.
    - wrap - memory wraps around on negative or too big index
    - abort - produces error on overflow/underflow
    - undefined - behavior undefined, overflow may cause segmentation fault
* cell size
    - byte - 8 bits
    - word - 16 bits
    - dword - 32 bits


TODOs:
* Add support for multiple targets


### Building
Project is written in Python 3 and has no external dependencies. Usage example:
```bash
python bfc/main.py examples/hello_world.bf > hello_world.asm
nasm -f elf64 hello_world.asm
ld -o hello_world hello_world.o
```

First argument is mandatory and defines Brainfuck source code file. Other arguments are optional - compiler target and compiler options in key=value form.

### Motivation
It's a one-evening project. I've got bored and implemented this compiler in a couple of hours. I'm planning to develop it further. Just for fun.

### Author
Jevgenijs Protopopovs

