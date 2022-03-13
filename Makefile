QEMU-FLAGS=#-bios /usr/share/ovmf/OVMF.fd
dd-flags=conv=notrunc
nasm-flags=


all: boot.img compile setup_fs
	qemu-system-x86_64 build/boot.img $(QEMU-FLAGS)

run:
	qemu-system-x86_64 build/boot.img $(QEMU-FLAGS)

update: compile run

update_all: compile update_kernel run

compile: boot.bin start.bin kernel.bin
	dd if=build/boot.bin of=build/boot.img bs=512 $(dd-flags) seek=0
	dd if=build/start.bin of=build/boot.img bs=512 $(dd-flags) seek=34

update_kernel:
	dd if=build/kernel.bin of=build/boot.img bs=512 $(dd-flags) seek=79


boot.img: src/disk.asm
	dd if=/dev/zero of=build/boot.img bs=1048576 count=128
	#nasm $< -o build/$@ $(nasm-flags)

boot.bin: src/boot/boot.asm
	nasm $< -o build/$@ $(nasm-flags)

start.bin: src/boot/start.asm
	nasm $< -o build/$@ $(nasm-flags)

kernel.bin: src/kernel/kernel.asm
	nasm $< -o build/$@ $(nasm-flags)

setup_fs:
	python3.10 setup.py build/boot.img
