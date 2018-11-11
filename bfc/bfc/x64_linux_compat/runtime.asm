DEFAULT REL

SECTION .data

BUF_SIZE:   Equ 24
WRITE_BUF:  times BUF_SIZE db 0
WRITE_POINTER: dq 0
MEMORY_SIZE dq  30000

SECTION .text

global MODULE_ENTRY

_bf_flush:
    mov rax, 1
    mov rdi, 0
    lea rsi, [WRITE_BUF]
    mov rdx, [WRITE_POINTER]
    syscall
    mov qword [WRITE_POINTER], 0
    ret

_bf_write:
    cmp qword [WRITE_POINTER], BUF_SIZE
    jl _bf_write_to_buf
    call _bf_flush
_bf_write_to_buf:
    mov rax, rdi
    lea rdi, [WRITE_BUF]
    add rdi, [WRITE_POINTER]
    mov [rdi], al
    inc qword [WRITE_POINTER]
	ret

_bf_read:
	call _bf_flush
	mov rax, 0
	mov rdi, 1
	push rdi
	lea rsi, [rsp]
	mov rdx, 1
	syscall
	pop rax
	ret

_bf_normalize_pointer:
    mov rax, rdi
	cmp rax, 0
	jge _bf_normalize_pointer_not_negative
	add rax, [MEMORY_SIZE]
_bf_normalize_pointer_not_negative:
	cmp rax, [MEMORY_SIZE]
	jl _bf_normalize_pointer_normal
	sub rax, [MEMORY_SIZE]
_bf_normalize_pointer_normal:
	ret

_bf_clear_memory:
    mov rax, 0
_bf_clear_memory_loop:
    mov byte [rsi + rax], 0
    inc rax
    cmp rax, rdi
    jne _bf_clear_memory_loop
	ret

MODULE_ENTRY:
    call _bf_clear_memory
    mov [MEMORY_SIZE], rdi
    push rbx
    push r12
    mov rbx, rsi
    call _bf_entry
    pop r12
    pop rbx
    call _bf_flush
    ret

