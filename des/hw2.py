# HW 2 
# By Michael Price

import sys
from BitVector import *

# Expansion permutation (See Section 3.3.1):
expansion_permutation = [31, 0, 1, 2, 3, 4, 3, 4, 5, 6, 7, 8, 7, 8, 
9, 10, 11, 12, 11, 12, 13, 14, 15, 16, 15, 16, 17, 18, 19, 20, 19, 
20, 21, 22, 23, 24, 23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31, 0]

# P-Box permutation (the last step of the Feistel function in Figure 4):
p_box_permutation = [15,6,19,20,28,11,27,16,0,14,22,25,4,17,30,9,
1,7,23,13,31,26,2,8,18,12,29,5,21,10,3,24]

# Initial permutation of the key (See Section 3.3.6):
key_permutation_1 = [56,48,40,32,24,16,8,0,57,49,41,33,25,17,9,1,58,
50,42,34,26,18,10,2,59,51,43,35,62,54,46,38,30,22,14,6,61,53,45,37,
29,21,13,5,60,52,44,36,28,20,12,4,27,19,11,3]

# Contraction permutation of the key (See Section 3.3.7):
key_permutation_2 = [13,16,10,23,0,4,2,27,14,5,20,9,22,18,11,3,25,
7,15,6,26,19,12,1,40,51,30,36,46,54,29,39,50,44,32,47,43,48,38,55,
33,52,45,41,49,35,28,31]

# Each integer here is the how much left-circular shift is applied
# to each half of the 56-bit key in each round (See Section 3.3.5):
shifts_key_halvs = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1] 




def assemble_sboxes():
	sboxs = []
	with open("s-box-tables.txt") as fp:
		for line in fp:
			if (line[0] != 'S') and (line[0] != '\n'):
				sbox = filter(None, line.strip('\n').split(' '))
				sboxs.append(sbox)
	return sboxs

def get_encryption_key():
	user_given_key = raw_input("Enter encryption key: ")
	while (len(user_given_key) != 8):
		print("Error: Encryption key must be 8 characters long. Try again.")
		user_given_key = raw_input("Enter encryption key: ")
	user_key_bv = BitVector(textstring = user_given_key)
	key_bv = user_key_bv.permute(key_permutation_1)
	return key_bv

def generate_round_keys(nkey):
	rkeys = []
	for i in range(16):
		[left, right] = nkey.divide_into_two()
		left << shifts_key_halvs[i]
		right << shifts_key_halvs[i]
		rejoined_key_bv = left + right
		rkey = rejoined_key_bv.permute(key_permutation_2)
		rkeys.append(rkey)
	return rkeys

def des(encrypt_or_decrypt, input_file, output_file, rkeys, sboxs):
	# Seperate encrypt and decrypt, use this function as means of sorting DES command

	bv_input = BitVector(filename = input_file)
	bv_block = bv_input.read_bits_from_file(64)
	bv_block_length = len(bv_block)
	#if (bv_block_length % 8) != 0:
	#	bv_block.pad_from_right(6 - (bv_block_length % 6))

	[LE, RE] = bv_block.divide_into_two()
	for i in range(16):
		RE_exp = RE.permute(expansion_permutation)			# E-Step
		xor_result = RE_exp ^ rkeys[i]						# Key mixing
		sbox_result = sbox_substitution(sboxs, xor_result)

		pbox_result = sbox_result.permute(p_box_permutation)
		right_half = LE ^ pbox_result

		LE = RE
		RE = right_half

	print(bv_block)
	print(LE + RE)


def sbox_substitution(sboxs, xor_result):
	new_bvs = BitVector(size = 0)
	for i in range(8):
		six_bits = xor_result[(i * 6):((i * 6) + 6)]
		inner_bits = six_bits[1:5]
		outer_bits = BitVector(bitlist = [six_bits[0], six_bits[5]])

		row = (i * 4) + int(outer_bits)
		column = int(inner_bits)

		new_val = sboxs[row][column]
		new_bv = BitVector(intVal = int(new_val), size = 4)
		
		new_bvs += new_bv
	return new_bvs

def pbox_permutation():
	pass

def main():
	sboxs = assemble_sboxes()
	nkey = get_encryption_key()
	rkeys = generate_round_keys(nkey)

	'''
	print(sboxs[0])
	print(sboxs[1])
	print(sboxs[2])
	print(sboxs[3])
	print(sboxs[4])
	print(sboxs[5])
	print(sboxs[6])
	print(sboxs[7])
	print(sboxs[8])
	print(sboxs[31])
	'''


	#bv48 = BitVector(bitstring = "010111010101011010101101010110100101000101001010")
	#sbox_substitution(sboxs, bv48)

	#key = "testeste"
	des(0, "message.txt", "test_out.txt", rkeys, sboxs)

if __name__ == "__main__":
	main()






