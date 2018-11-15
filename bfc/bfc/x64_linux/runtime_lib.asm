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
    lea rsi, [rel WRITE_BUF]
    mov rdx, [rel WRITE_POINTER]
    syscall
    mov qword [rel WRITE_POINTER], 0
    ret

_bf_write:
    cmp qword [rel WRITE_POINTER], BUF_SIZE
    jl _bf_write_to_buf
    call _bf_flush
_bf_write_to_buf:
    lea rdi, [rel WRITE_BUF]
    add rdi, [rel WRITE_POINTER]
    mov rax, [rbx + r12]
    mov [rdi], al
    inc qword [rel WRITE_POINTER]
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
    mov rax, [rel MEMORY_SIZE]
    imul rax, BF_CELL_SIZE
	cmp r12, 0
	jge _bf_normalize_pointer_not_negative
	add r12, rax
_bf_normalize_pointer_not_negative:
	cmp r12, rax
	jl _bf_normalize_pointer_normal
	sub r12, rax
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
    cmp r12, [rel MEMORY_SIZE]
    jge _bf_abort
    ret
%endif

_bf_clear_memory:
    mov rcx, 0
    mov rax, rdi
    imul rax, BF_CELL_SIZE
_bf_clear_memory_loop:
    mov byte [rsi + rcx], 0
    inc rcx
    cmp rcx, rax
    jne _bf_clear_memory_loop
	ret

MODULE_ENTRY:
    call _bf_clear_memory
    mov [rel MEMORY_SIZE], rdi
    push rbx
    push r12
    mov rbx, rsi
    call _bf_entry
    pop r12
    pop rbx
    cmp rax, 0
    jne _bf_on_error
    call _bf_flush
    mov rax, 0
_bf_on_error:
    ret

