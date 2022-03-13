%ifndef STRING
%define STRING

%include "src/include/port.asm"
%include "src/include/util.asm"

%define VIDEO_ADDRESS 0xb8000
%define MAX_ROWS 25 ; y
%define MAX_COLS 80 ; x


; char, attr, x, y
print_char_at:
	push rbp
	mov rbp, rsp
	add rbp, 8 * 2
	push rbx

	push qword [rbp + 8 * 3] ; y
	push qword [rbp + 8 * 2] ; x
	call get_offset
	add rsp, 8 * 2

	mov bl, [rbp + 8 * 0]
	mov bh, [rbp + 8 * 1]

	cmp bl, 0x0a ; \n
	je .new_line

	cmp bl, 0x0d ; \r
	je .return

	mov rbp, VIDEO_ADDRESS
	add rbp, rax

	mov [rbp], bx

	add rax, 2

	jmp .end

.new_line:
	add rax, MAX_COLS * 2

	jmp .end

.return:
	mov rax, [rbp + 8 * 3]
	mov rbx, MAX_COLS
	mul rbx
	shl rax, 1

.end:
	pop rbx
	pop rbp
ret


; str, attr, x, y
print_at:
	push rbp
	mov rbp, rsp
	add rbp, 8 * 2
	push rbx
	push rsi

	mov rsi, [rbp + 8 * 0] ; str

	push qword [rbp + 8 * 3] ; y
	push qword [rbp + 8 * 2] ; x
	call get_offset
	add rsp, 8 * 2

	mov rbx, rax

.loop:
	cmp byte [rsi], 0
	jz .end

	push rbx
	call get_offset_row
	add rsp, 8

	push rax

	push rbx
	call get_offset_col
	add rsp, 8

	push rax

	push qword [rbp + 8 * 1] ; attr
	push qword [rsi]
	call print_char_at
	add rsp, 8 * 4

	mov rbx, rax
	inc rsi

	jmp .loop

.end:
	pop rsi
	pop rbx
	pop rbp
ret


; str, attr
print:
	push rbp
	mov rbp, rsp
	add rbp, 8 * 2
	push rbx
	push rsi

	mov rsi, [rbp + 8 * 0] ; str

.loop:
	cmp byte [rsi], 0
	jz .end

	call get_cursor_pos
	mov rbx, rax

	push rbx
	call get_offset_row
	add rsp, 8

	push rax

	push rbx
	call get_offset_col
	add rsp, 8

	push rax

	push qword [rbp + 8 * 1] ; attr
	push qword [rsi]
	call print_char_at
	add rsp, 8 * 4

	push rax
	call set_cursor_pos
	add rsp, 8

	inc rsi

	jmp .loop

.end:
	pop rsi
	pop rbx
	pop rbp
ret


clear_screen:
	push qword MAX_COLS * MAX_ROWS
	push qword 0x0f00
	push qword VIDEO_ADDRESS
	call memset_word
	pop rax
	pop rax
	pop rax
ret



; int col, int row
; return (row * MAX_COLS + col) * 2
get_offset:
	push rbp
	mov rbp, rsp
	add rbp, 8 * 2
	push rbx

	mov rax, [rbp + 8 * 1] ; row
	mov rbx, MAX_COLS
	mul rbx

	add rax, [rbp + 8 * 0] ; row

	shl rax, 1

	pop rbx
	pop rbp
ret


; int offset
; return offset / (MAX_COLS * 2)
get_offset_row:
	push rbx
	push rdx

	mov rax, [rsp + 8 * 3] ; offset
	mov rdx, 0

	mov rbx, MAX_COLS
	shl rbx, 1

	div rbx

	pop rdx
	pop rbx
ret

; int offset
; return (offset - get_offset_row(offset) * MAX_COLS * 2) / 2
get_offset_col:
	push rbp
	push rbx
	push rdx

	push qword [rsp + 8 * 4] ; offset
	call get_offset_row
	add rsp, 8

	mov rbx, MAX_COLS
	mul rbx

	shl rax, 1

	mov rbx, [rsp + 8 * 4] ; offset
	sub rbx, rax

	shr rbx, 1

	mov rax, rbx

	pop rdx
	pop rbx
	pop rbp
ret

; int offset
set_cursor_pos:
	push rbp
	push rbx

	mov rbp, rsp

	mov rbx, [rbp + 8 * 3 + 0] ; offset

	shr rbx, 1 ; offset /= 2

	push rbx

	and rbx, 0xff

	push qword 0x0f
	push qword 0x3d4
	call set_port_byte
	add rsp, 8 * 2

	push qword rbx
	push qword 0x3d5
	call set_port_byte
	add rsp, 8 * 2

	pop rbx

	and rbx, 0xff00

	shr rbx, 8

	push qword 0x0e
	push qword 0x3d4
	call set_port_byte
	add rsp, 8 * 2

	push qword rbx
	push qword 0x3d5
	call set_port_byte
	add rsp, 8 * 2

	pop rbx
	pop rbp
ret


get_cursor_pos:
	push rbx

	mov rbx, 0

	push qword 0x0f
	push qword 0x3d4
	call set_port_byte
	add rsp, 8 * 2

	push qword 0x3d5
	call get_port_byte
	add rsp, 8

	mov rbx, rax

	push qword 0x0e
	push qword 0x3d4
	call set_port_byte
	add rsp, 8 * 2

	push qword 0x3d5
	call get_port_byte
	add rsp, 8

	shl rax, 8
	add rbx, rax

	mov rax, rbx

	shl rax, 1

	pop rbx
ret


%endif