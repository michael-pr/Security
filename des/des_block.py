# HW 2 
# Problem 1
# By Michael Price

# Usage: 
#	
# 	Standard:		python DES_Price.py
#   Encryption:		python DES_Price.py <input_file> <output_file> <key_file> -e
# 	Decryption:  	python DES_Price.py <input_file> <output_file> <key_file> -d

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


def get_input_file():
	input_file = raw_input("Input file: ")
	return input_file


def get_output_file():
	output_file = raw_input("Output file: ")
	return output_file


def get_encrypt_or_decrypt():
	encrypt_or_decrypt = ""
	while (encrypt_or_decrypt != 'e') and (encrypt_or_decrypt != 'd'):
		encrypt_or_decrypt = raw_input("Encrypt or decrypt (E/D): ")
		encrypt_or_decrypt = encrypt_or_decrypt.lower()
	return encrypt_or_decrypt


def get_encryption_key():
	# Get user key and run it through first round of permutation
	user_given_key = raw_input("Enter encryption key: ")
	while (len(user_given_key) < 8):
		print("Error: Encryption key must be 8 characters long. Try again.")
		user_given_key = raw_input("Enter encryption key: ")
	key_bv = initial_key_perm(user_given_key)
	return key_bv


def initial_key_perm(key_string):
	user_key_bv = BitVector(textstring = key_string)
	return user_key_bv.permute(key_permutation_1)


def assemble_sboxes(s_box_filename):
	# Read sbox files and generate a table
	sboxs = []
	with open(s_box_filename) as fp:
		for line in fp:
			if (line[0] != 'S') and (line[0] != '\n'):
				sbox = filter(None, line.strip('\n').split(' '))
				sboxs.append(sbox)
	return sboxs


def generate_round_keys(nkey):
	# Generate the round keys for each round as a table
	rkeys = []
	for i in range(16):
		[left, right] = nkey.divide_into_two()
		left << shifts_key_halvs[i]
		right << shifts_key_halvs[i]
		rejoined_key_bv = left + right
		rkey = rejoined_key_bv.permute(key_permutation_2)
		rkeys.append(rkey)
	return rkeys


def expansion_perm(re):
	return re.permute(expansion_permutation)


def sbox_substitution(sboxs, xor_result):
	# sbox substituion for 48bit to 32bit
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


def pbox_perm(sbox_result):
	return sbox_result.permute(p_box_permutation)


def des(encrypt_or_decrypt, bv_input, result_bv, nkey, sboxs):
	rkeys = generate_round_keys(nkey)

	if(encrypt_or_decrypt == 'd'):
		rkeys = rkeys[::-1]											# Reverse the round keys if decryption
	else: pass

	while (True):
		try:
			bv_block = bv_input.read_bits_from_file(64)				# Read 64 bits from input file
		except:
			bv_block = bv_input.read_bits_from_fileobject(64)		# For testing purposes
		if (len(bv_block) == 0):
			break													# End of input file
		if (len(bv_block) < 64):									# Catch non 8 byte multiples
			if (encrypt_or_decrypt == 'd'):
				raise ValueError("Currupted cipher-text. Try again.")
			else:
				bv_block.pad_from_right(64 - len(bv_block))			# Pad bit block 
		else: pass

		# If decryption 
		if (encrypt_or_decrypt == 'd'):
			[RE, LE] = bv_block.divide_into_two()
		else:
			[LE, RE] = bv_block.divide_into_two()

		# Perform Feistel Function
		for i in range(16):
			expansion_result = expansion_perm(RE)					# Expansion permutaion
			xor_result = expansion_result ^ rkeys[i]				# Xor result with round key			
			sbox_result = sbox_substitution(sboxs, xor_result)		# Sbox substitution
			pbox_result = pbox_perm(sbox_result)					# Pbox permutation
			right_half = LE ^ pbox_result							# Final Xor

			LE = RE
			RE = right_half

		# If decryption switch left and right
		if (encrypt_or_decrypt == 'd'):
			result_bv += (RE + LE)
		else:
			result_bv += (LE + RE)

	return result_bv


def init_des():
	# Check use of program
	if (len(sys.argv) != 5):
		input_file = get_input_file()
		output_file = get_output_file()
		encrypt_or_decrypt = get_encrypt_or_decrypt()
		nkey = get_encryption_key()
	else:
		input_file = sys.argv[1]
		output_file = sys.argv[2]
		
		with open(sys.argv[3]) as fp:
			key = [x.strip('\n') for x in fp.readlines()]
			key = ''.join(key)
			if (len(key) != 8):
				sys.exit("Error: Encryption key must be 8 characters long. Please modify your key file and try again.")
			user_key_bv = BitVector(textstring = key)
			nkey = user_key_bv.permute(key_permutation_1)	

		encrypt_or_decrypt = sys.argv[4][1]

		if (encrypt_or_decrypt != 'e') and (encrypt_or_decrypt != 'd'):
			sys.exit("Usage: python DES_Price.py <input_file> <output_file> <key_file> -e/d")

	# Initialize input file as bit vector
	bv_input = BitVector(filename = input_file)
	file_out = open(output_file, 'wb')
	result_bv = BitVector(size = 0)

	sboxs = assemble_sboxes("s-box-tables.txt")

	if (encrypt_or_decrypt == "e"):
		print("Implementing DES encryption on '%s'..." % input_file)
	else:
		print("Implementing DES decryption on '%s'..." % input_file)

	# Begin either encryption/decryption
	result_bv = des(encrypt_or_decrypt, bv_input, result_bv, nkey, sboxs)

	if (encrypt_or_decrypt == "e"):
		print("Writing cipher-text to '%s'..." % output_file)
	else:
		print("Writing plain-text to '%s'..." % output_file)

	result_bv.write_to_file(file_out)

	print("DES complete!")

	bv_input.close_file_object()
	file_out.close()


def main():
	if (len(sys.argv) != 5) and (len(sys.argv) != 1):
		sys.exit("Usage: python DES_Price.py")
	init_des()


if __name__ == "__main__":
	main()






