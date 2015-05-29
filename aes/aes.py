# AES
# By Michael Price

#
# Usage: $ python aes.py
#

import sys
from BitVector import *

DEFAULT_INPUT_FILE = "plaintext.txt"
DEFAULT_D_OUTPUT_FILE = "decryptedtext.txt"
DEFAULT_E_OUTPUT_FILE = "encryptedtext.txt"
DEFAULT_KEY = "lukeimyourfather"

def build_state_array(block):
	state_array = [[0 for x in range(4)] for x in range(4)]
	for i in range(4):
		for j in range(4):
			state_array[j][i] = block[32*i + 8*j:32*i + 8*(j+1)]
	return state_array


def build_key_state_array(key):
	key_bv = BitVector(textstring = key)
	return build_state_array(key_bv)

def state_array_to_block(state_array):
	block_state_array = zip(*state_array)
	new_block = BitVector(size = 0)
	for row_item in block_state_array:
		for column_item in row_item:
			new_block = new_block + column_item
	return new_block


#
# Key scheudle building
#

def build_key_schedule_0_3(state_array):
	# Inialize key schedule, w0-w3
	flipped_state_array = zip(*state_array)
	key_schedule = []
	empty_bv = BitVector(size = 0)
	for i in range(4):
		key_schedule.append(empty_bv)
		for j in range(4):
			key_schedule[i] = key_schedule[i] + flipped_state_array[i][j]

	return key_schedule


def build_key_schedule(key_schedule_0_3, s_box): #round_key_0):
	# Build the rest of the keys, w4-w43
	
	key_schedule = []
	for i in range(4):
		key_schedule.append(key_schedule_0_3[i])

	for i in range(10):
		i_round = i * 4
		w_i_4 = key_schedule[i_round] ^ g_function(key_schedule[i_round + 3], i, s_box)
		w_i_5 = w_i_4 ^ key_schedule[i_round + 1]
		w_i_6 = w_i_5 ^ key_schedule[i_round + 2]
		w_i_7 = w_i_6 ^ key_schedule[i_round + 3]

		key_schedule.append(w_i_4)
		key_schedule.append(w_i_5)
		key_schedule.append(w_i_6)
		key_schedule.append(w_i_7)

	return key_schedule
	
def g_function(word, round_num, s_box):
	# one-byte left circular rotation
	for i in range(8):
		word.circular_rotate_left_by_one()

	# Perform byte substitution for each byte of the word --> SubBytes
	new_word = BitVector(size = 0)
	for i in range(4):
		byte_idx = (i * 8)
		row = int(word[byte_idx:(byte_idx + 4)])
		col = int(word[(byte_idx + 4):(byte_idx + 8)])
		new_word = new_word + BitVector(intVal = s_box[row][col], size = 8)

	word = new_word

	# Xor with round constant
	AES_modulus = BitVector(bitstring = "100011011")
	n = 8
	empty_bv = BitVector(size = 24)
	if ((round_num) > 0):
		rcj1 = BitVector(size = 0)
		rc = BitVector(hexstring = "02")
		
		for i in range(round_num, 0, -1): 		#for (i = round_num; i > 0; i--):
			if (i != 1):
				rcj1 = BitVector(hexstring = "02")
			else:
				rcj1 = BitVector(hexstring = "01")
			rc = rc.gf_multiply_modular(rcj1, AES_modulus, n)
	else:
		rc = BitVector(hexstring = "01")
	
	round_constant = rc + empty_bv

	word = word ^ round_constant

	return word

#
# SubBytes
#

def sub_bytes(block, s_box):
	return sub_block(block, s_box)

def inv_sub_bytes(block, s_box):
	return sub_block(block, s_box)

def sub_byte(byte, s_box):
	byte_idx = (i * 8)
	row = int(block[0:4])
	col = int(block[4:8])
	return BitVector(intVal = s_box[row][col], size = 8)

def sub_block(block, s_box):
	# Start bit scrambling
	new_block = BitVector(size = 0)
	for i in range(16):
		byte_idx = (i * 8)
		row = int(block[byte_idx:(byte_idx + 4)])
		col = int(block[(byte_idx + 4):(byte_idx + 8)])
		new_block = new_block + BitVector(intVal = s_box[row][col], size = 8)
	return new_block
			
def build_s_box(encrypt_or_decrypt):
	AES_modulus = BitVector(bitstring='100011011')
	c = BitVector(bitstring='01100011')
	d = BitVector(bitstring='00000101')

	new_sub_bytes = []
	if (encrypt_or_decrypt == 'e'):
		for i in range(0, 256):
			# Build lookup table
			a = BitVector(intVal = i, size=8).gf_MI(AES_modulus, 8) if i != 0 else BitVector(intVal=0)
			# Byte scrambling
			a1,a2,a3,a4 = [a.deep_copy() for x in range(4)]
			a ^= (a1 >> 4) ^ (a2 >> 5) ^ (a3 >> 6) ^ (a4 >> 7) ^ c
			new_sub_bytes.append(int(a))
	else:
		for i in range(0, 256):
			b = BitVector(intVal = i, size=8)
			# byte scrambling
			b1,b2,b3 = [b.deep_copy() for x in range(3)]
			b = (b1 >> 2) ^ (b2 >> 5) ^ (b3 >> 7) ^ d
			check = b.gf_MI(AES_modulus, 8)
			b = check if isinstance(check, BitVector) else 0
			new_sub_bytes.append(int(b))

	sub_byte_table = []
	for i in range(16):
		sub_byte_table.append([])
		for j in range(16):
			sub_byte_table[i].append(new_sub_bytes[(i * 16) + j])

	return sub_byte_table

#
# Shift rows
#

def shift_rows(block):
	state_array = build_state_array(block)
	shifted = []
	for i in range(4):
		shifted.append([])
		for j in range(4):
			if (i == 0):
				shifted[i].append( state_array[i][j] )
			elif (i == 1):
				shifted[i].append( state_array[i][(j + 1) % 4] )
			elif (i == 2):	
				shifted[i].append( state_array[i][(j + 2) % 4] )
			elif (i == 3):
				shifted[i].append( state_array[i][(j + 3) % 4] )
	return state_array_to_block(shifted)


def inv_shift_rows(block):
	state_array = build_state_array(block)
	shifted = []
	for i in range(4):
		shifted.append([])
		for j in range(4):
			if (i == 0):
				shifted[i].append( state_array[i][j] )
			elif (i == 1):
				shifted[i].append( state_array[i][(j + 3) % 4] )
			elif (i == 2):	
				shifted[i].append( state_array[i][(j + 2) % 4] )
			elif (i == 3):
				shifted[i].append( state_array[i][(j + 1) % 4] )
	return state_array_to_block(shifted)


#
# Mix columns
#
def mix_columns(block):
	state_array = build_state_array(block)
	AES_modulus = BitVector(bitstring = "100011011")
	n = 8

	hex_02 = BitVector(hexstring = "02")
	hex_03 = BitVector(hexstring = "03")

	mixed = []
	for i in range(4):
		mixed.append([])
		for j in range(4):
			if (i == 0):
				hex_02_result = state_array[0][j].gf_multiply_modular(hex_02, AES_modulus, n)
				hex_03_result = state_array[1][j].gf_multiply_modular(hex_03, AES_modulus, n)
				new_byte = (hex_02_result) ^ (hex_03_result) ^ state_array[2][j] ^ state_array[3][j]
				mixed[i].append( new_byte )
			elif (i == 1):
				hex_02_result = state_array[1][j].gf_multiply_modular(hex_02, AES_modulus, n)
				hex_03_result = state_array[2][j].gf_multiply_modular(hex_03, AES_modulus, n)
				new_byte = (hex_02_result) ^ (hex_02_result) ^ state_array[0][j] ^ state_array[3][j]
				mixed[i].append( new_byte )
			elif (i == 2):
				hex_02_result = state_array[2][j].gf_multiply_modular(hex_02, AES_modulus, n)
				hex_03_result = state_array[3][j].gf_multiply_modular(hex_03, AES_modulus, n)
				new_byte = (hex_02_result) ^ (hex_02_result) ^ state_array[0][j] ^ state_array[1][j]
				mixed[i].append( new_byte )
			elif (i == 3):
				hex_02_result = state_array[3][j].gf_multiply_modular(hex_02, AES_modulus, n)
				hex_03_result = state_array[0][j].gf_multiply_modular(hex_03, AES_modulus, n)
				new_byte = (hex_02_result) ^ (hex_02_result) ^ state_array[1][j] ^ state_array[2][j]
				mixed[i].append( new_byte )

	return state_array_to_block(mixed)


def inv_mix_columns(block):
	state_array = build_state_array(block)
	AES_modulus = BitVector(bitstring = "100011011")
	n = 8

	hex_0E = BitVector(hexstring = "03")
	hex_0B = BitVector(hexstring = "0b")
	hex_0D = BitVector(hexstring = "0d")
	hex_09 = BitVector(hexstring = "09")

	mixed = []
	for i in range(4):
		mixed.append([])
		for j in range(4):
			if (i == 0):
				hex_0E_result = state_array[0][j].gf_multiply_modular(hex_0E, AES_modulus, n)
				hex_0B_result = state_array[1][j].gf_multiply_modular(hex_0B, AES_modulus, n)
				hex_0D_result = state_array[2][j].gf_multiply_modular(hex_0D, AES_modulus, n)
				hex_09_result = state_array[3][j].gf_multiply_modular(hex_09, AES_modulus, n)
				new_byte = (hex_0E_result) ^ (hex_0B_result) ^ (hex_0D_result) ^ (hex_09_result)
				mixed[i].append( new_byte )
			elif (i == 1):
				hex_0E_result = state_array[1][j].gf_multiply_modular(hex_0E, AES_modulus, n)
				hex_0B_result = state_array[2][j].gf_multiply_modular(hex_0B, AES_modulus, n)
				hex_0D_result = state_array[3][j].gf_multiply_modular(hex_0D, AES_modulus, n)
				hex_09_result = state_array[0][j].gf_multiply_modular(hex_09, AES_modulus, n)
				new_byte = (hex_0E_result) ^ (hex_0B_result) ^ (hex_0D_result) ^ (hex_09_result)
				mixed[i].append( new_byte )
			elif (i == 2):
				hex_0E_result = state_array[2][j].gf_multiply_modular(hex_0E, AES_modulus, n)
				hex_0B_result = state_array[3][j].gf_multiply_modular(hex_0B, AES_modulus, n)
				hex_0D_result = state_array[0][j].gf_multiply_modular(hex_0D, AES_modulus, n)
				hex_09_result = state_array[1][j].gf_multiply_modular(hex_09, AES_modulus, n)
				new_byte = (hex_0E_result) ^ (hex_0B_result) ^ (hex_0D_result) ^ (hex_09_result)
				mixed[i].append( new_byte )
			elif (i == 3):
				hex_0E_result = state_array[3][j].gf_multiply_modular(hex_0E, AES_modulus, n)
				hex_0B_result = state_array[0][j].gf_multiply_modular(hex_0B, AES_modulus, n)
				hex_0D_result = state_array[1][j].gf_multiply_modular(hex_0D, AES_modulus, n)
				hex_09_result = state_array[2][j].gf_multiply_modular(hex_09, AES_modulus, n)
				new_byte = (hex_0E_result) ^ (hex_0B_result) ^ (hex_0D_result) ^ (hex_09_result)
				mixed[i].append( new_byte )

	return state_array_to_block(mixed)

#
# encrype/decrypt functions
# 

def encrypt(input_file, s_box, key_schedule):
	input_bv = BitVector(filename = input_file)
	ciphertext_bv = BitVector(size = 0)

	while (True):
		try: new_block = input_bv.read_bits_from_file(128)
		except: break

		if (len(new_block) < 128): break

		# Xor first 128-bits with first four words of key schedule
		combined_words = (key_schedule[0] + key_schedule[1] + key_schedule[2] + key_schedule[3])
		new_block = new_block ^ combined_words

		# Start round processing, i denotes the round
		for i in range(1, 11):
			if (i != 10):
				# Substitute bytes
				new_block = sub_bytes(new_block, s_box)
				# Shift rows
				new_block = shift_rows(new_block)
				# Mix columns
				new_block = mix_columns(new_block)
				# Add round key
				combined_words = (key_schedule[i * 4] + key_schedule[(i * 4) + 1] + key_schedule[(i * 4) + 2] + key_schedule[(i * 4) + 3])
				new_block = new_block ^ combined_words
			else:
				# Substitute bytes
				new_block = sub_bytes(new_block, s_box)
				# Shift rows
				new_block = shift_rows(new_block)
				# Add round key
				combined_words = (key_schedule[i * 4] + key_schedule[(i * 4) + 1] + key_schedule[(i * 4) + 2] + key_schedule[(i * 4) + 3])
				new_block = new_block ^ combined_words

		ciphertext_bv = ciphertext_bv + new_block

	return ciphertext_bv



def decrypt(input_file, s_box, key_schedule):
	input_bv = BitVector(filename = input_file)
	plaintext_bv = BitVector(size = 0)

	while (True):
		try: 
			new_block = input_bv.read_bits_from_file(128)
		except: break

		if (len(new_block) < 128): break

		# Xor first 128-bits with first four words of key schedule
		combined_words = (key_schedule[40] + key_schedule[41] + key_schedule[42] + key_schedule[43])
		new_block = new_block ^ combined_words

		count_down = 9
		for i in range(1, 11):
			if (i != 10):
				# Inverse shift rows
				new_block = inv_shift_rows(new_block)
				# Invsere substitute bytes
				new_block = inv_sub_bytes(new_block, s_box)
				# Add round key
				combined_words = (key_schedule[count_down * 4] + key_schedule[(count_down * 4) + 1] + key_schedule[(count_down * 4) + 2] + key_schedule[(count_down * 4) + 3])
				new_block = new_block ^ combined_words
				# Inverse mix columns
				new_block = inv_mix_columns(new_block)
			else:
				# Inverse shift rows
				new_block = inv_shift_rows(new_block)
				# Invsere substitute bytes
				new_block = inv_sub_bytes(new_block, s_box)
				# Add round key
				combined_words = (key_schedule[count_down * 4] + key_schedule[(count_down * 4) + 1] + key_schedule[(count_down * 4) + 2] + key_schedule[(count_down * 4) + 3])
				new_block = new_block ^ combined_words
			count_down = count_down - 1

		plaintext_bv = plaintext_bv + new_block

	return plaintext_bv

def main():
	# Encryption
	s_box = build_s_box('e')

	key_state_array = build_key_state_array(DEFAULT_KEY)
	key_schedule_0_3 = build_key_schedule_0_3(key_state_array)
	key_schedule = build_key_schedule(key_schedule_0_3, s_box)
	
	cipher_text = encrypt(DEFAULT_INPUT_FILE, s_box, key_schedule)


	e_output = open(DEFAULT_E_OUTPUT_FILE, 'wb')
	cipher_text.write_to_file(e_output)
	#e_output.write(str(cipher_text))
	e_output.close()

	# Decryption
	s_box = build_s_box('d')
	
	plain_text = decrypt(DEFAULT_E_OUTPUT_FILE, s_box, key_schedule)

	d_output = open(DEFAULT_D_OUTPUT_FILE, 'wb')
	#plain_text.write_to_file(d_output)
	d_output.write(plain_text.get_text_from_bitvector())
	d_output.close()
	

if __name__ == "__main__":
	main()