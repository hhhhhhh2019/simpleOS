%ifndef PORT
%define PORT

; int port
get_port_byte:
	push rbp
	push rdx

	mov rbp, rsp

	mov dx, [rbp + 8 * 3] ; port
	mov rax, 0

	in al, dx

	pop rdx
	pop rbp
ret

; int port, int data
set_port_byte:
	push rbp
	push rdx

	mov rbp, rsp

	mov rax, 0

	mov dx, [rbp + 8 * 3 + 8 * 0] ; port
	mov ax, [rbp + 8 * 3 + 8 * 1] ; data

	out dx, al

	pop rdx
	pop rbp
ret

; int port
get_port_word:
	push rbp
	push rdx

	mov rbp, rsp

	mov rdx, [rbp + 8 * 3] ; port
	mov rax, 0

	in al, dx

	pop rdx
	pop rbp
ret

; int port, int data
set_port_word:
	push rbp
	push rdx

	mov rbp, rsp

	mov rax, 0

	mov rdx, [rbp + 8 * 3 + 8 * 0] ; port
	mov rax, [rbp + 8 * 3 + 8 * 1] ; data

	out dx, ax

	pop rdx
	pop rbp
ret

%endif