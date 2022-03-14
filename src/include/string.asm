%ifndef STRING
%define STRING

%include "src/include/screen.asm"

;char* str
str_len:
	push rbp
	
	mov rbp, [rsp + 8 * 2 + 0]

	mov rax, 0

.loop:
	cmp byte [rbp], 0
	je .end

	inc rax
	inc rbp
jmp .loop

.end
	pop rbp
ret


; char* str1, char* str2, int count
; 1 - ok, 0 - rrror
arr_cmp:
	push rbp
	push rsi
	push rbx

	mov rbp, [rsp + 8 * 4 + 8 * 0]
	mov rsi, [rsp + 8 * 4 + 8 * 1]
	mov rax, [rsp + 8 * 4 + 8 * 2]

.loop:
	cmp rax, 0
	je .ok

	mov byte bl, [rbp]
	mov byte bh, [rsi]

	cmp bl, bh
	jne .error

	inc rbp
	inc rsi
	dec rax
jmp .loop

.ok:
	mov rax, 1
	jmp .end

.error:
	mov rax, 0

.end:
	  pop rbx
	pop rsi
	pop rbp
ret



%endif
