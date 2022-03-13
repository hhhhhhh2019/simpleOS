%ifndef DISK
%define DISK

%define ATA_BASE 0x1f0
%define ATA_CONTROL 0x3f4

%define IDE_BSY       0x80
%define IDE_DRDY      0x40
%define IDE_DF        0x20
%define IDE_ERR       0x01

%define IDE_CMD_READ  0x20
%define IDE_CMD_WRITE 0x30
%define IDE_CMD_RDMUL 0xc4
%define IDE_CMD_WRMUL 0xc5


; addr, count, buffer
read_sector:
	push rbp
	mov rbp, rsp
	add rbp, 8 * 2
	push rcx
	push rdx


	mov rax, [rbp + 8 * 1] ; count
	mov dx, ATA_BASE + 2
	out dx, al


	mov rax, [rbp + 8 * 0] ; addr
	mov dx, ATA_BASE + 3
	out dx, al

	mov rax, [rbp + 8 * 0] ; addr
	shr rax, 8
	mov dx, ATA_BASE + 4
	out dx, al

	mov rax, [rbp + 8 * 0] ; addr
	shr rax, 16
	mov dx, ATA_BASE + 5
	out dx, al

	mov rax, [rbp + 8 * 0] ; addr
	shr rax, 8
	and al, 0x0f
	or al, 0xe0
	mov dx, ATA_BASE + 6
	out dx, al

	mov dx, ATA_BASE + 7
	mov al, IDE_CMD_READ
	out dx, al

.loop:
	in al, dx
	test al, 8
	jz .loop

	mov rcx, [rbp + 8 * 1]
	shl rcx, 8
	mov rbp, [rbp + 8 * 2] ; buffer

.read_loop:
	mov dx, ATA_BASE
	in ax, dx

	mov [rbp], al
	mov [rbp + 1], ah

	add rbp, 2

	dec rcx

	cmp rcx, 0
	jne .read_loop


	pop rdx
	pop rcx
	pop rbp
ret

%endif