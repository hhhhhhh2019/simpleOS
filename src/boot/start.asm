[org 0x500]
[bits 64]


[map all start.map]

jmp start

%include "src/include/screen.asm"
%include "src/include/disk.asm"
;%include "src/include/fs.asm"


start:
	call clear_screen

	jmp $