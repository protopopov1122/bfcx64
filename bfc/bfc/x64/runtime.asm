SECTION .text

MEMORY_SIZE:	Equ	30000

global _start

_bf_terminate:
	mov rax, 60
	syscall

_bf_write:
	mov rax, 1
	push rdi
	mov rdi, 0
	lea rsi, [rsp]
	mov rdx, 1
	syscall
	pop rdi
	ret

_bf_read:
	mov rax, 0
	mov rdi, 1
	push rdi
	lea rsi, [rsp]
	mov rdx, 1
	syscall
	pop rax
	ret

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
	mov rcx, MEMORY_SIZE
_bf_alloc_loop:
	mov byte [rdi], 0
	inc rdi
	dec rcx
	jnz _bf_alloc_loop
	ret

_start:
	call _bf_alloc
	mov rdi, rax
	call _bf_entry
	jmp _bf_terminate

