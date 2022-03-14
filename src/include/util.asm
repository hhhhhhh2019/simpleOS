%ifndef UTIL
%define UTIL

; int from, int to, int count
memcpy:
	push rbp
	mov rbp, rsp
	add rbp, 8 * 2
	push rbx
	push rcx
	push rdx

	mov rcx, [rbp + 8 * 2] ; count
	mov rbx, [rbp + 8 * 0] ; from
	mov rdx, [rbp + 8 * 1] ; to

.loop: 
	mov al, [rbx]
	mov byte [rdx], al

	inc rdx
	inc rbx

	dec rcx

	cmp rcx, 0
	jg .loop


	pop rdx
	pop rcx
	pop rbx
	pop rbp
ret


; *mem, char value, int count
memset:
	push rcx
	push rbp
	push rbx

	mov rbp, [rsp + 8 * 4 + 8 * 0]
	mov rbx, [rsp + 8 * 4 + 8 * 1]
	mov rcx, [rsp + 8 * 4 + 8 * 2]


.loop:
	mov [rbp], bl
	inc rbp
	dec rcx

	cmp rcx, 0
	jne .loop
	
	pop rbx
	pop rbp
	pop rcx
ret

; *mem, int16 value, int count
memset_word:
	push rbp
	mov rbp, rsp
	add rbp, 8 * 2
	push rbx
	push rcx

	mov rcx, [rbp + 8 * 2] ; count
	mov rbx, [rbp + 8 * 1] ; value
	mov rbp, [rbp + 8 * 0] ; mem

.loop:
	mov word [rbp], bx

	add rbp, 2
	dec rcx

	cmp rcx, 0
	jne .loop

	pop rcx
	pop rbx
	pop rbp
ret


; addr, size
init_hdt:
	push rbx

	mov rbx, [rsp + 8 * 2 + 8 * 0] ; addr
	mov rax, rbx
	add rax, 393216 + 4 + 4 + 2
	mov dword [rbx], eax

	mov rax, [rbp + 8 * 2 + 8 * 1] ; size

	mov dword [rbx + 4], eax

	mov word [rbx + 8], 0

	pop rbx
ret

; *hdt, size
malloc:

ret


%endif