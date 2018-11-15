%define ERROR_MESSAGE "Brainfuck error: memory overflow. Aborting"
%strlen ERROR_MESSAGE_LEN ERROR_MESSAGE

SECTION .data

BUF_SIZE:       Equ 24
WRITE_BUF:      times BUF_SIZE db 0
WRITE_POINTER:  dq 0
ERROR_MESSAGE_DB:  db 10, ERROR_MESSAGE, 10, 0

SECTION .text

MEMORY_SIZE:	Equ	30000 * BF_CELL_SIZE

global _start


_bf_on_error:
    mov rax, 1
    mov rdi, 0
    lea rsi, [ERROR_MESSAGE_DB]
    mov rdx, ERROR_MESSAGE_LEN
    add rdx, 2
    syscall

_bf_terminate:
	mov rax, 60
	syscall

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
    lea rdi, [WRITE_BUF]
    add rdi, [WRITE_POINTER]
    mov rax, [rbx + r12]
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
	mov [rbx+r12], al
	ret

%if BF_WRAP_ON_OVERFLOW=1
_bf_normalize_pointer:
	cmp r12, 0
	jge _bf_normalize_pointer_not_negative
	add r12, MEMORY_SIZE
_bf_normalize_pointer_not_negative:
	cmp r12, MEMORY_SIZE
	jl _bf_normalize_pointer_normal
	sub r12, MEMORY_SIZE
_bf_normalize_pointer_normal:
	ret
%endif


%if BF_ABORT_ON_OVERFLOW=1
_bf_abort:
    add rsp, 8
    mov rax, 1
    ret

_bf_check_pointer:
    cmp r12, 0
    jl _bf_abort
    cmp r12, MEMORY_SIZE
    jge _bf_abort
    ret
%endif

_bf_alloc:
	mov rax, 12
	mov rdi, 0
	syscall
	push rax
	mov rdi, rax
	add rdi, MEMORY_SIZE
	mov rax, 12
	syscall
	pop rax
	mov rdi, rax
	mov rbx, rax
	mov rcx, MEMORY_SIZE
_bf_alloc_loop:
	mov byte [rdi], 0
	inc rdi
	dec rcx
	jnz _bf_alloc_loop
	ret

_start:
	call _bf_alloc
	call _bf_entry
	cmp rax, 0
	jne _bf_on_error
	call _bf_flush
	jmp _bf_terminate

