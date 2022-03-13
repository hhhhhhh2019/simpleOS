def arr2num(arr):
	res = 0

	for i in range(len(arr)):
		res |= arr[i] << (i * 8)
	
	return res

def num2arr(num, l):
	res = []

	for i in range(l):
		res.append((num >> (i * 8)) & 0xff)
	
	return res

def malloc(hdt, size):
	ok = False
	addr = 0

	if arr2num(data[hdt + 8:hdt + 10]) == 0:
		ok = True
	
	elif arr2num(data[hdt + 8:hdt + 10]) == 65535:
		return None
	
	elif arr2num(data[hdt + 10:hdt + 14]) >= size:
			ok = True
	
	if not ok:
		for i in range(arr2num(data[hdt + 8:hdt + 10]) - 1):
			a = arr2num(data[hdt + 10 + i * 6:10 + i * 6 + 4]) + arr2num(data[hdt + 10 + i * 6 + 4:hdt + 10 + i * 6 + 4 + 2])
			b = arr2num(data[hdt + 10 + i * 6 + 6:hdt + 10 + i * 6 + 6 + 4])

			if b - a >= size:
				ok = True
				addr = a
				break

	if not ok:
		c = arr2num(data[hdt + 8:hdt + 10]) - 1
		a = arr2num(data[hdt + 10 + c * 6:hdt + 10 + c * 6 + 4]) + arr2num(data[hdt + 10 + c * 6 + 4:hdt + 10 + c * 6 + 4 + 2])
		b = arr2num(data[hdt + 0:hdt + 4]) + arr2num(data[hdt + 4:hdt + 8])

		if b - a >= size:
			ok = True
			addr = a
	
	if not ok:
		return None
	

	c = arr2num(data[hdt + 8:hdt + 10])
	data[hdt + 10 + c * 6:hdt + 10 + c * 6 + 4] = num2arr(addr, 4)
	data[hdt + 10 + c * 6 + 4:hdt + 10 + c * 6 + 4 + 2] = num2arr(size, 2)
	data[hdt + 8:hdt + 10] = num2arr(c + 1, 2)

	return addr + arr2num(data[hdt + 0:hdt + 4])


def free(hdt, addr):
	addr -= arr2num(data[hdt+0:hdt+4])
	elemid = None

	for i in range(arr2num(data[hdt + 8:hdt + 10])):
		if arr2num(data[hdt + 10 + i * 6:hdt + 10 + i * 6 + 4]) == addr:
			elemid = i
			break
	
	if not elemid == None:
		tmp = data[hdt + 10 + elemid * 6 + 6:arr2num(data[hdt+0:hdt+4])]
		for i in range(len(tmp)):
			data[hdt + 10 + elemid * 6 + i] = tmp[i]

		data[hdt + 8:hdt + 10] = num2arr(arr2num(data[hdt + 8:hdt + 10]) - 1, 2)


def print_elems(hdt):
	for i in range(arr2num(data[hdt + 8:hdt + 10])):
		print(arr2num(data[hdt + 10 + i * 6:hdt + 10 + i * 6 + 4]), arr2num(data[hdt + 10 + i * 6 + 4:hdt + 10 + i * 6 + 4 + 2]))


data = [0] * 1024 * 1024 * 4


# init hdt
data[0:4] = num2arr(393216 + 10, 4)
data[4:8] = num2arr(len(data) - 393216 - 10, 4)
data[8:10] = num2arr(0, 2)


a = malloc(0, 64)
b = malloc(0, 4 * 30)
c = malloc(0, 512 * 10)

print_elems(0)
print()

free(0, b)

d = malloc(0, 4 * 25)

print_elems(0)
