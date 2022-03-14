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


	jmp 0x500

times 512-($-$$)-2 db 0
dw 0xaa55
