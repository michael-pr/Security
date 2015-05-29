import sys
from BitVector import *
import random
import DES_Price

bv1 = BitVector(bitstring = "110101")
bv2 = BitVector(bitstring = "100001")
bv3 = BitVector(bitstring = "100111")
bv4 = BitVector(bitstring = "000001")

bv48 = BitVector(bitstring = "010111010101011010101101010110100101000101001010")

six_bits = bv1[1:5]
outer_bits = BitVector(bitlist = [bv1[0], bv1[5]])

bv3 = BitVector(intVal = 15, size = 4)

vals = BitVector(size = 0)

vals += bv1
vals += bv2
vals += bv3
vals += bv4

'''
bv_file = BitVector(filename = "test.txt")

for i in range(600):
	tmp = bv_file.read_bits_from_file(64)
	print(tmp)
	if (len(tmp) < 64) and (len(tmp) > 0):
		if (len(tmp) % 8) != 0:
			tmp.pad_from_right(8 - (len(tmp) % 8))
		print("Last line extended (if needed)")
		print(tmp)
		break
'''
bv_string = BitVector(textstring = "Security companies recorded millions of attacks and probes related to the bug in the days following the disclosu")
bv64_1 = BitVector(bitstring = "0110110001101111011100110111010101110010011001010010111000000000")
bv64_2 = BitVector(bitstring = "0110011000010000010000000101001100010111010001011111101111100011")
#print(str(bv64_1.get_text_from_bitvector()))
#print(str(bv64_2.get_text_from_bitvector()))
#print(len(bv_string))

'''
with open("key.txt") as fp:
	key = [x.strip('\n') for x in fp.readlines()]
	key = ''.join(key)
	print(key)
'''

'''
with open("message.txt") as fp:
	content = ''.join(fp.readlines())
	bv_content = BitVector(textstring = content)
	print (len(bv_content))

bv_file = BitVector(filename = "message.txt")
bv_new = BitVector(size = 0)
while (True):
	bv_bit = bv_file.read_bits_from_file(8)
	if (len(bv_bit) == 0):
		break
	if (len(bv_bit) < 8):
		bv_new += bv_bit[0:len(bv_bit)]
	else:
		bv_new += bv_bit
print (len(bv_new))
# They are the same!!!!!! value!!!!! lol awesome
'''

'''
test = 0
test = 1 if (test == 1) else 2
print (test)
'''
'''
import io
x = "111100001111"
fp_read = io.StringIO(unicode(x))
bv = BitVector(fp = fp_read)
print(bv)
'''

for i in range(4):
	sbox_file = open("sbox_test_case" + str(i) + ".txt", 'w')
	for j in range(8):
		if (j != 0):
			sbox_file.write("\n")
		sbox_file.write("S" + str(j + 1) + ":\n\n")
		for z in range(4):
			for w in range(16):
				sbox_file.write(str(random.randint(0, 15)) + " ")
			sbox_file.write("\n")

test = []
for i in range(4):
	print "sbox_test_case" + str(i) + ".txt"
	try:
		sbox = DES_Price.assemble_sboxes("sbox_test_case" + str(i) + ".txt")
		test.append(sbox)
	except: pass

	if (i == (3)):
		test.pop()

print test
#for item in test:
#	print item[0]


#bv_file.close_file_object()
#print(str(six_bits), str(outer_bits))
#print(int(six_bits), int(outer_bits))
#print(bv3)
#print(vals)