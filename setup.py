import sys
from zlib import crc32
from uuid import uuid4


MIN_SIZE = 0


H = 255
S = 63

def guid2num(guid):
	d1 = (guid & 0xff) << 24 | (guid >> 8 & 0xff) << 16 | (guid >> 16 & 0xff) << 8 | (guid >> 24 & 0xff)
	guid = guid >> 32
	d2 = (guid & 0xff) << 8 | (guid >> 8 & 0xff)
	guid = guid >> 16
	d3 = (guid & 0xff) << 8 | (guid >> 8 & 0xff)
	guid = guid >> 16
	d4 = (guid & 0xff) << 8 | (guid >> 8 & 0xff)
	guid = guid >> 16
	d5 = (guid & 0xff) << 40 | (guid >> 8 & 0xff) << 32 | (guid << 16 & 0xff) << 24 | (guid >> 24 & 0xff) << 16 | (guid >> 32 & 0xff) << 8 | (guid >> 40 & 0xff)

	return d1 << 56 | d2 << 24 | d3 << 16 | d4 << 8 | d5

def lba(s,h,c):
	return (c * H + h) * S + (s - 1)

def sch(nlba):
	s = (nlba % S) + 1
	h = (nlba - (s - 1)) // S % H
	c = (nlba - (s - 1) - h * S) // (H * S)

	return (s,h-1,c)

def num2lba(num):
	return num // 512

def size_input(ask):
	ok = False

	while not ok:
		inp = input(ask)

		delim = 0

		for i in inp:
			if not i.isnumeric():
				break

			delim += 1

		if inp == '':
			ok = False
			continue

		if not inp[0:delim].isnumeric():
			continue

		num = int(inp[0:delim])
		unit = inp[delim:len(inp)].lower()

		ok = True

		if unit == "":
			ok == False
			continue
		elif unit == "kb" or unit == "кб":
			num *= 1024
		elif unit == "mb" or unit == "мб":
			num *= 1024 * 1024
		elif unit == "gb" or unit == "гб":
			num *= 1024 * 1024 * 1024
		else:
			print("Неизвестный тип!")
			ok = False
			continue

	return num


def int_input(ask, mi=0, ma=0):
	res = ""
	in_range = True

	while not res.isnumeric() or not in_range or res == '':
		if not res == "" and not res.isnumeric():
			print("Введите целое число!")

		res = input(ask)

		if res == '':
			continue

		if res.isnumeric() and mi != 0 and ma != 0:
			if not (mi >= int(res) >= ma):
				print("Число должно быть в диапозоне от: " + str(mi) + ' - ' + str(ma))
				in_range = False
				continue
			else:
				in_range = True

	return int(res)

def num2size(num):
	if num < 1024 * 1024:
		return str(num / 1024) + "КБ"
	elif num < 1024 * 1024 * 1024:
		return str(num / 1024 / 1024) + "МБ"
	else:
		return str(num / 1024 / 1024 / 1024) + "ГБ"


def bool_input(ask):
	while True:
		inp = input(ask + "(д/н): ").lower()

		if (inp == 'y' or inp == 'д' or inp == ''):
			return True
		
		if (inp == 'n' or inp == 'н'):
			return False


def make_simple_fs(start_lba, size):
	offset = start_lba * 512

	for i in range(8):
		data[offset + i] = (0x5af615a7bfe90bd4 >> i * 8) & 0xff


	for i in range(8):
		data[offset + 8 + i] = num2lba(offset) >> i * 8 & 0xff

	for i in range(8):
		data[offset + 16 + i] = num2lba(offset + size) >> i * 8 & 0xff
	

	for i in range(512 - 26):
		data[offset + 8 + 18 + i] = 0
	
	for i in range(512*8):
		data[offset + 512 + i] = 0xff



file_name = ''

if len(sys.argv) > 1:
	file_name = sys.argv[1]
	print("Образ диска: " + str(file_name))
else:
	file_name = input("Образ диска: ")

print("")

file = open(file_name, mode="br")

data = list(file.read())

file.close()

disk_size = len(data)

print("Размер диска: " + num2size(disk_size))

end_lba = num2lba(disk_size) - 1

print("\n\nНастройка gpt")

data[0x1be + 0] = 0
data[0x1be + 1] = 0 # head
data[0x1be + 2] = 2 # cylinder
data[0x1be + 3] = 0 # sector
data[0x1be + 4] = 0xee # type
data[0x1be + 5] = sch(end_lba)[0]
data[0x1be + 6] = sch(end_lba)[1]
data[0x1be + 7] = sch(end_lba)[2]
data[0x1be + 8] = 1
data[0x1be + 9] = 0
data[0x1be + 10] = 0
data[0x1be + 11] = 0
data[0x1be + 12] = end_lba & 0xff
data[0x1be + 13] = end_lba >> 8 & 0xff
data[0x1be + 14] = end_lba >> 16 & 0xff
data[0x1be + 15] = end_lba >> 32 & 0xff

data[510] = 0x55
data[511] = 0xaa


gpt_lba = 1
table_lba = num2lba(512 * 2)
gpt_copy_lba = end_lba
table_copy_lba = num2lba(disk_size - 512 * 35)

start_usable_lba = num2lba(512 + 512 * 34)
end_usable_lba = num2lba(disk_size - 512 - 512 * 34)

disk_guid = guid2num(int(uuid4()))



gpt_sign = "EFI PART"
for i in range(len(gpt_sign)):
	data[512 + i] = ord(gpt_sign[i])

data[512 + 0x8 + 0] = 0
data[512 + 0x8 + 1] = 0
data[512 + 0x8 + 2] = 1
data[512 + 0x8 + 3] = 0

data[512 + 0xc + 0] = 92
data[512 + 0xc + 1] = 0
data[512 + 0xc + 2] = 0
data[512 + 0xc + 3] = 0

data[512 + 0x10 + 0] = 0 # header hash
data[512 + 0x10 + 1] = 0 # header hash
data[512 + 0x10 + 2] = 0 # header hash
data[512 + 0x10 + 3] = 0 # header hash

data[512 + 0x14 + 0] = 0 # reserved
data[512 + 0x14 + 1] = 0 # reserved
data[512 + 0x14 + 2] = 0 # reserved
data[512 + 0x14 + 3] = 0 # reserved

data[512 + 0x18 + 0] =  gpt_lba & 0xff
data[512 + 0x18 + 1] = (gpt_lba >> 8) & 0xff
data[512 + 0x18 + 2] = (gpt_lba >> 16) & 0xff
data[512 + 0x18 + 3] = (gpt_lba >> 24) & 0xff
data[512 + 0x18 + 4] = (gpt_lba >> 32) & 0xff
data[512 + 0x18 + 5] = (gpt_lba >> 40) & 0xff
data[512 + 0x18 + 6] = (gpt_lba >> 48) & 0xff
data[512 + 0x18 + 7] = (gpt_lba >> 56) & 0xff

data[512 + 0x20 + 0] =  gpt_copy_lba & 0xff
data[512 + 0x20 + 1] = (gpt_copy_lba >> 8) & 0xff
data[512 + 0x20 + 2] = (gpt_copy_lba >> 16) & 0xff
data[512 + 0x20 + 3] = (gpt_copy_lba >> 24) & 0xff
data[512 + 0x20 + 4] = (gpt_copy_lba >> 32) & 0xff
data[512 + 0x20 + 5] = (gpt_copy_lba >> 40) & 0xff
data[512 + 0x20 + 6] = (gpt_copy_lba >> 48) & 0xff
data[512 + 0x20 + 7] = (gpt_copy_lba >> 56) & 0xff

data[512 + 0x20 + 0] =  gpt_copy_lba & 0xff
data[512 + 0x20 + 1] = (gpt_copy_lba >> 8) & 0xff
data[512 + 0x20 + 2] = (gpt_copy_lba >> 16) & 0xff
data[512 + 0x20 + 3] = (gpt_copy_lba >> 24) & 0xff
data[512 + 0x20 + 4] = (gpt_copy_lba >> 32) & 0xff
data[512 + 0x20 + 5] = (gpt_copy_lba >> 40) & 0xff
data[512 + 0x20 + 6] = (gpt_copy_lba >> 48) & 0xff
data[512 + 0x20 + 7] = (gpt_copy_lba >> 56) & 0xff


data[512 + 0x28 + 0] =  start_usable_lba & 0xff
data[512 + 0x28 + 1] = (start_usable_lba >> 8) & 0xff
data[512 + 0x28 + 2] = (start_usable_lba >> 16) & 0xff
data[512 + 0x28 + 3] = (start_usable_lba >> 24) & 0xff
data[512 + 0x28 + 4] = (start_usable_lba >> 32) & 0xff
data[512 + 0x28 + 5] = (start_usable_lba >> 40) & 0xff
data[512 + 0x28 + 6] = (start_usable_lba >> 48) & 0xff
data[512 + 0x28 + 7] = (start_usable_lba >> 56) & 0xff

data[512 + 0x30 + 0] =  end_usable_lba & 0xff
data[512 + 0x30 + 1] = (end_usable_lba >> 8) & 0xff
data[512 + 0x30 + 2] = (end_usable_lba >> 16) & 0xff
data[512 + 0x30 + 3] = (end_usable_lba >> 24) & 0xff
data[512 + 0x30 + 4] = (end_usable_lba >> 32) & 0xff
data[512 + 0x30 + 5] = (end_usable_lba >> 40) & 0xff
data[512 + 0x30 + 6] = (end_usable_lba >> 48) & 0xff
data[512 + 0x30 + 7] = (end_usable_lba >> 56) & 0xff


data[512 + 0x38 + 0]  =  disk_guid & 0xff
data[512 + 0x38 + 1]  = (disk_guid >> 8) & 0xff
data[512 + 0x38 + 2]  = (disk_guid >> 16) & 0xff
data[512 + 0x38 + 3]  = (disk_guid >> 24) & 0xff
data[512 + 0x38 + 4]  = (disk_guid >> 32) & 0xff
data[512 + 0x38 + 5]  = (disk_guid >> 40) & 0xff
data[512 + 0x38 + 6]  = (disk_guid >> 48) & 0xff
data[512 + 0x38 + 7]  = (disk_guid >> 56) & 0xff
data[512 + 0x38 + 8]  = (disk_guid >> 64) & 0xff
data[512 + 0x38 + 9]  = (disk_guid >> 72) & 0xff
data[512 + 0x38 + 10] = (disk_guid >> 80) & 0xff
data[512 + 0x38 + 11] = (disk_guid >> 88) & 0xff
data[512 + 0x38 + 12] = (disk_guid >> 96) & 0xff
data[512 + 0x38 + 13] = (disk_guid >> 104) & 0xff
data[512 + 0x38 + 14] = (disk_guid >> 112) & 0xff
data[512 + 0x38 + 15] = (disk_guid >> 120) & 0xff


data[512 + 0x48 + 0] =  table_lba & 0xff
data[512 + 0x48 + 1] = (table_lba >> 8) & 0xff
data[512 + 0x48 + 2] = (table_lba >> 16) & 0xff
data[512 + 0x48 + 3] = (table_lba >> 24) & 0xff
data[512 + 0x48 + 4] = (table_lba >> 32) & 0xff
data[512 + 0x48 + 5] = (table_lba >> 40) & 0xff
data[512 + 0x48 + 6] = (table_lba >> 48) & 0xff
data[512 + 0x48 + 7] = (table_lba >> 56) & 0xff

data[512 + 0x50 + 0] = 0 # number of partition entries
data[512 + 0x50 + 1] = 0 # number of partition entries
data[512 + 0x50 + 2] = 0 # number of partition entries
data[512 + 0x50 + 3] = 0 # number of partition entries

data[512 + 0x54 + 0] =  128 & 0xff
data[512 + 0x54 + 1] = (128 >> 8) & 0xff
data[512 + 0x54 + 2] = (128 >> 16) & 0xff
data[512 + 0x54 + 3] = (128 >> 24) & 0xff

data[512 + 0x58 + 0] = 0 # table hash
data[512 + 0x58 + 1] = 0 # table hash
data[512 + 0x58 + 2] = 0 # table hash
data[512 + 0x58 + 3] = 0 # table hash

print("")



partitions_guids = [
	guid2num(0x00000000000000000000000000000000),
	guid2num(0xff3ab5f74a004566b72167570e1c7604),
]

partitions_names = [
	'пустой раздел',
	'раздел с данными'
]

fs_names = [
	'simple fs'
]



partitions_count = 0
free_space = disk_size - 512 * 35 * 2
next_free_lba = 36

while free_space > MIN_SIZE and bool_input("Создать раздел?"):	
	type_guid = 0
	type_id = 0
	guid = guid2num(int(uuid4()))

	start_lba = next_free_lba
	end_lba = 0
	size = 0

	attr = 0

	name = ""



	print("Свободного места:", num2size(free_space))

	size = size_input("Размер раздела: ")
	
	while (size > free_space):
		print("Свободного места меньше!")
		if bool_input("Устанлвить размер раздела в " + num2size(free_space) + "?"):
			size = free_space
			break
		size = size_input("Размер раздела: ")
	
	if not size % 512 == 0:
		size += 512 - size % 512

	

	name = input("Имя раздела: ")
	


	print("Типы раделов:")

	for i in range(len(partitions_names)):
		print("\t" + str(i) + " " + partitions_names[i])
	
	type_id = int_input("Тип раздела: ")
	
	while type_id >= len(partitions_names):
		type_id = int_input("Тип раздела: ")


	type_guid = partitions_guids[type_id]

	if type_id == 1:
		print("Типы файловых систем:")

		for i in range(len(fs_names)):
			print("\t" + str(i) + " " + fs_names[i])
		
		type_id = int_input("Тип файловой системы: ")
		
		while type_id >= len(fs_names):
			type_id = int_input("Тип файловой системы: ")
		
		if type_id == 0:
			make_simple_fs(start_lba, size)
			type

	end_lba = start_lba + size // 512
	free_space -= size
	next_free_lba += size // 512 + 1


	data[1024 + partitions_count * 128 + 0]  =  type_guid & 0xff
	data[1024 + partitions_count * 128 + 1]  = (type_guid >> 8) & 0xff
	data[1024 + partitions_count * 128 + 2]  = (type_guid >> 16) & 0xff
	data[1024 + partitions_count * 128 + 3]  = (type_guid >> 24) & 0xff
	data[1024 + partitions_count * 128 + 4]  = (type_guid >> 32) & 0xff
	data[1024 + partitions_count * 128 + 5]  = (type_guid >> 40) & 0xff
	data[1024 + partitions_count * 128 + 6]  = (type_guid >> 48) & 0xff
	data[1024 + partitions_count * 128 + 7]  = (type_guid >> 56) & 0xff
	data[1024 + partitions_count * 128 + 8]  = (type_guid >> 64) & 0xff
	data[1024 + partitions_count * 128 + 9]  = (type_guid >> 72) & 0xff
	data[1024 + partitions_count * 128 + 10] = (type_guid >> 80) & 0xff
	data[1024 + partitions_count * 128 + 11] = (type_guid >> 88) & 0xff
	data[1024 + partitions_count * 128 + 12] = (type_guid >> 96) & 0xff
	data[1024 + partitions_count * 128 + 13] = (type_guid >> 104) & 0xff
	data[1024 + partitions_count * 128 + 14] = (type_guid >> 112) & 0xff
	data[1024 + partitions_count * 128 + 15] = (type_guid >> 120) & 0xff

	data[1024 + partitions_count * 128 + 16 + 0]  =  guid & 0xff
	data[1024 + partitions_count * 128 + 16 + 1]  = (guid >> 8) & 0xff
	data[1024 + partitions_count * 128 + 16 + 2]  = (guid >> 16) & 0xff
	data[1024 + partitions_count * 128 + 16 + 3]  = (guid >> 24) & 0xff
	data[1024 + partitions_count * 128 + 16 + 4]  = (guid >> 32) & 0xff
	data[1024 + partitions_count * 128 + 16 + 5]  = (guid >> 40) & 0xff
	data[1024 + partitions_count * 128 + 16 + 6]  = (guid >> 48) & 0xff
	data[1024 + partitions_count * 128 + 16 + 7]  = (guid >> 56) & 0xff
	data[1024 + partitions_count * 128 + 16 + 8]  = (guid >> 64) & 0xff
	data[1024 + partitions_count * 128 + 16 + 9]  = (guid >> 72) & 0xff
	data[1024 + partitions_count * 128 + 16 + 10] = (guid >> 80) & 0xff
	data[1024 + partitions_count * 128 + 16 + 11] = (guid >> 88) & 0xff
	data[1024 + partitions_count * 128 + 16 + 12] = (guid >> 96) & 0xff
	data[1024 + partitions_count * 128 + 16 + 13] = (guid >> 104) & 0xff
	data[1024 + partitions_count * 128 + 16 + 14] = (guid >> 112) & 0xff
	data[1024 + partitions_count * 128 + 16 + 15] = (guid >> 120) & 0xff

	data[1024 + partitions_count * 128 + 32 + 0] =  start_lba & 0xff
	data[1024 + partitions_count * 128 + 32 + 1] = (start_lba >> 8) & 0xff
	data[1024 + partitions_count * 128 + 32 + 2] = (start_lba >> 16) & 0xff
	data[1024 + partitions_count * 128 + 32 + 3] = (start_lba >> 24) & 0xff
	data[1024 + partitions_count * 128 + 32 + 4] = (start_lba >> 32) & 0xff
	data[1024 + partitions_count * 128 + 32 + 5] = (start_lba >> 40) & 0xff
	data[1024 + partitions_count * 128 + 32 + 6] = (start_lba >> 48) & 0xff
	data[1024 + partitions_count * 128 + 32 + 7] = (start_lba >> 56) & 0xff
	
	data[1024 + partitions_count * 128 + 40 + 0] =  end_lba & 0xff
	data[1024 + partitions_count * 128 + 40 + 1] = (end_lba >> 8) & 0xff
	data[1024 + partitions_count * 128 + 40 + 2] = (end_lba >> 16) & 0xff
	data[1024 + partitions_count * 128 + 40 + 3] = (end_lba >> 24) & 0xff
	data[1024 + partitions_count * 128 + 40 + 4] = (end_lba >> 32) & 0xff
	data[1024 + partitions_count * 128 + 40 + 5] = (end_lba >> 40) & 0xff
	data[1024 + partitions_count * 128 + 40 + 6] = (end_lba >> 48) & 0xff
	data[1024 + partitions_count * 128 + 40 + 7] = (end_lba >> 56) & 0xff


	data[1024 + partitions_count * 128 + 48 + 0] = 0
	data[1024 + partitions_count * 128 + 48 + 1] = 0
	data[1024 + partitions_count * 128 + 48 + 2] = 0
	data[1024 + partitions_count * 128 + 48 + 3] = 0
	data[1024 + partitions_count * 128 + 48 + 4] = 0
	data[1024 + partitions_count * 128 + 48 + 5] = 0
	data[1024 + partitions_count * 128 + 48 + 6] = 0
	data[1024 + partitions_count * 128 + 48 + 7] = 0

	for i in range(72):
		if i < len(name):
			data[1024 + partitions_count * 128 + 56 + i] = ord(name[i])
		else:
			data[1024 + partitions_count * 128 + 56 + i] = 0
	
	partitions_count += 1



data[512 + 0x50 + 0] =  partitions_count & 0xff
data[512 + 0x50 + 1] = (partitions_count >> 8) & 0xff
data[512 + 0x50 + 2] = (partitions_count >> 16) & 0xff
data[512 + 0x50 + 3] = (partitions_count >> 24) & 0xff

gpt_hash = crc32(bytearray(data[512:512 + 92]))
table_hash = crc32(bytearray(data[1024:1024 + partitions_count * 128]))

data[512 + 0x10 + 0] =  gpt_hash & 0xff
data[512 + 0x10 + 1] = (gpt_hash >> 8) & 0xff
data[512 + 0x10 + 2] = (gpt_hash >> 16) & 0xff
data[512 + 0x10 + 3] = (gpt_hash >> 24) & 0xff

data[512 + 0x58 + 0] =  table_hash & 0xff
data[512 + 0x58 + 1] = (table_hash >> 8) & 0xff
data[512 + 0x58 + 2] = (table_hash >> 16) & 0xff
data[512 + 0x58 + 3] = (table_hash >> 24) & 0xff



for i in range(512):
	data[gpt_copy_lba * 512 + i] = data[512 + i]

for i in range(512 * 34):
	data[gpt_copy_lba * 512 - 512 * 35 + i] = data[512 * 34 + i]


file = open(file_name, mode="bw")
file.write(bytearray(data))
file.close()