[org 0x7c00]
[bits 16]

mov [boot_disk], dl

jmp start

boot_disk: db 0

gdt32_start:

gdt32_null:
	dd 0
	dd 0

gdt32_code:
	dw 0xffff
	dw 0x0
	db 0x0
	db 10011010b
	db 11001111b
	db 0x0

gdt32_data:
	dw 0xffff
	dw 0x0
	db 0x0
	db 10010010b
	db 11001111b
	db 0x0

gdt32_end:

gdt32_descriptor:
	dw gdt32_end - gdt32_start - 1
	dd gdt32_start

CODE32_SEG equ gdt32_code - gdt32_start
DATA32_SEG equ gdt32_data - gdt32_start




PRESENT        equ 1 << 7
NOT_SYS        equ 1 << 4
EXEC           equ 1 << 3
DC             equ 1 << 2
RW             equ 1 << 1
ACCESSED       equ 1 << 0
 
; Flags bits
GRAN_4K       equ 1 << 7
SZ_32         equ 1 << 6
LONG_MODE     equ 1 << 5
 
GDT:
	.Null: equ $ - GDT
		dq 0
	.Code: equ $ - GDT
		dd 0xFFFF                                   ; Limit & Base (low, bits 0-15)
		db 0                                        ; Base (mid, bits 16-23)
		db PRESENT | NOT_SYS | EXEC | RW            ; Access
		db GRAN_4K | LONG_MODE | 0xF                ; Flags & Limit (high, bits 16-19)
		db 0                                        ; Base (high, bits 24-31)
	.Data: equ $ - GDT
		dd 0xFFFF                                   ; Limit & Base (low, bits 0-15)
		db 0                                        ; Base (mid, bits 16-23)
		db PRESENT | NOT_SYS | RW                   ; Access
		db GRAN_4K | SZ_32 | 0xF                    ; Flags & Limit (high, bits 16-19)
		db 0                                        ; Base (high, bits 24-31)
	.TSS: equ $ - GDT
		dd 0x00000068
		dd 0x00CF8900
	.Pointer:
		dw $ - GDT - 1
		dq GDT



start:
	mov ah, 0x02
	mov bh, 0
	mov dh, 0
	mov dl, 0
	int 0x10

	mov ax, 0
	mov es, ax
	mov bx, 0x500
	mov ah, 02h ; read sector
	mov dl, 80h
	mov dh, 0
	mov ch, 0
	mov cl, 35 ; sector + 1
	mov al, 20 ; sectors count
	int 13h

	cli
	lgdt [gdt32_descriptor]

	mov eax, cr0
	or eax, 1
	mov cr0, eax

	jmp CODE32_SEG:init

[bits 32]
init:
	mov ax, DATA32_SEG
	mov ds, ax
	mov ss, ax
	mov es, ax
	mov fs, ax
	mov gs, ax


	; init long mode
	pushfd
	pop eax

	mov ecx, eax
	xor eax, 1 << 21

	push eax
	popfd

	pushfd
	pop eax

	push ecx
	popfd

	xor eax, ecx
	jz NoCPUID

	mov eax, 0x80000000
	cpuid
	cmp eax, 0x80000001
	jb NoLongMode

	mov eax, 0x80000001
	cpuid
	test edx, 1 << 29
	jz NoLongMode


	mov eax, cr0
	and eax, 01111111111111111111111111111111b
	mov cr0, eax


	mov edi, 0x1000
	mov cr3, edi
	xor eax, eax
	mov ecx, 4096
	rep stosd
	mov edi, cr3


	mov DWORD [edi], 0x2003
	add edi, 0x1000
	mov DWORD [edi], 0x3003
	add edi, 0x1000
	mov DWORD [edi], 0x4003
	add edi, 0x1000

	mov ebx, 0x00000003
	mov ecx, 512

.SetEntry:
	mov DWORD [edi], ebx
	add ebx, 0x1000
	add edi, 8
	loop .SetEntry


	mov eax, cr4
	or eax, 1 << 5
	mov cr4, eax


	mov ecx, 0xC0000080
	rdmsr
	or eax, 1 << 8
	wrmsr


	mov eax, cr0
	or eax, 1 << 31
	mov cr0, eax


	lgdt [GDT.Pointer]         ; Load the 64-bit global descriptor table.
	jmp GDT.Code:init64

NoCPUID:
	mov byte [0xb8000], 'C'
	mov byte [0xb8000 + 2], 'P'
	mov byte [0xb8000 + 4], 'U'
	mov byte [0xb8000 + 6], 'I'
	mov byte [0xb8000 + 8], 'D'
	mov byte [0xb8000 + 10], 0
	jmp $

NoLongMode:
	mov byte [0xb8000], 'N'
	mov byte [0xb8000 + 2], 'O'
	mov byte [0xb8000 + 4], ' '
	mov byte [0xb8000 + 6], 'L'
	mov byte [0xb8000 + 8], 'O'
	mov byte [0xb8000 + 10], 'N'
	mov byte [0xb8000 + 12], 'G'
	mov byte [0xb8000 + 14], ' '
	mov byte [0xb8000 + 16], 'M'
	mov byte [0xb8000 + 18], 'O'
	mov byte [0xb8000 + 20], 'D'
	mov byte [0xb8000 + 22], 'E'
	mov byte [0xb8000 + 24], 0
	jmp $


[bits 64]
init64:
	mov ax, GDT.Data
	mov ds, ax
	mov ss, ax
	mov es, ax
	mov fs, ax
	mov gs, ax

	mov ebp, 0x90000
	mov rsp, rbp

	jmp 0x500

times 512-($-$$)-2 db 0
dw 0xaa55
