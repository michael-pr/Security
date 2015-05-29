# HW 2
# Problem 2
# By Michael Price

# Step 1: Determine effects of diffusion
# Find the average of diffusion for 100 test runs

# Usage:
#	python Average_Price.py <input_file> <number_of_test_cases>

# Notes: Had trouble with using FileObjects to pass to DES routine
#
#	test = StringIO.StringIO(content)
#	input_bv_fp = BitVector(fp = test)
#
#		ValueError: invalid literal for int() with base 10: 'S'
#
# Therefore will have to read/write files in order to complete the task

import sys
import StringIO
from BitVector import *
import DES_Price
import random

#
# Program Start
#

if len(sys.argv) is not 3:
	sys.exit("Usage: python Average_Price.py <input_file> <number_of_test_cases>")

NUM_TEST_CASES = int(sys.argv[2])

print("Initializing test variables...")
print("Test cases: %d" % NUM_TEST_CASES)

input_filename = sys.argv[1]

# Get original message bit-vector
content = ""
with open(input_filename) as fp: #sys.argv[1]) as fp:
	content = ''.join(fp.readlines())


input_bv = BitVector(textstring = content)
input_bv_fp = BitVector(filename = input_filename)

# Get original cipher-text bit-vector
key = "sherlock"
nkey = DES_Price.initial_key_perm(key)

try:
	sboxs = DES_Price.assemble_sboxes("s-box-tables.txt")
except:
	sys.exit("Cannot find default s-box file: 's-box-tables.txt'")

empty_bv = BitVector(size = 0)
original_encrypted_bv = DES_Price.des('e', input_bv_fp, empty_bv, nkey, sboxs)

print("Default key: %s" % key)
print("Original cipher-text bit length: %d" % len(original_encrypted_bv))

#
# Diffusion Test: Compare original cipher-text with cipher-text of test cases where single bits were changed
#

print("\nProcessing diffusion tests...")

# Create test cases (modified plaintext bits into cipher-text)

test_cases = []
for i in range(NUM_TEST_CASES):
	new_input_bv = input_bv[:]
	new_input_bv[i] = 1 if (new_input_bv[i] == 0) else 0
	test_cases.append(new_input_bv)

# Write test cases to files for DES processing
for i in range(NUM_TEST_CASES):
	test_case_fp = open("test_case" + str(i) + ".txt", 'wb')
	test_cases[i].write_to_file(test_case_fp)
	test_case_fp.close()

# Get cipher-text for all test cases
test_cases_encrypted = []
for i in range(NUM_TEST_CASES):
	empty_bv = BitVector(size = 0)
	test_case_bv_fp = BitVector(filename = ("test_case" + str(i) + ".txt"))
	new_encrypted_bv = DES_Price.des('e', test_case_bv_fp, empty_bv, nkey, sboxs)
	test_cases_encrypted.append(new_encrypted_bv)

for i in range(NUM_TEST_CASES):
	test_case_ciphertext_fp = open("test_case_ct" + str(i) + ".txt", 'wb')
	test_cases_encrypted[i].write_to_file(test_case_ciphertext_fp)
	test_case_ciphertext_fp.close()

# Compare original cipher-text to test case cipher-texts to measure diffusion
num_changed_bits_per_diff_test = []

for i in range(NUM_TEST_CASES):
	num_changed_bits_per_diff_test.append(0)

length_of_cipher_text = len(test_cases_encrypted[0])
for i in range(NUM_TEST_CASES):
	# Loop through bits and compare
	for j in range(length_of_cipher_text):
		num_changed_bits_per_diff_test[i] += 1 if (test_cases_encrypted[i][j] != original_encrypted_bv[j]) else 0

diffusion_average = 0
for item in num_changed_bits_per_diff_test:
	diffusion_average += item
diffusion_average = diffusion_average / NUM_TEST_CASES
diffusion_percentage = (diffusion_average / length_of_cipher_text) * 100

print("There was an average of %d bits changed from the original cipher-text when bits were changed in the plaintext" % diffusion_average)

#
# Confusion Test: Compare cipher-text test cases when encryption key has changed with original cipher-text
#

print("\nProcessing confusion tests...")

# Create test cases (modified encryption keys) *Assuming number of test cases does not overflow 8 character key
key_bv = BitVector(textstring = key)
modified_keys = []
for i in range(NUM_TEST_CASES):
	new_key_bv = key_bv[:]
	new_key_bv[i] = 1 if (new_key_bv[i] == 0) else 0
	modified_keys.append(new_key_bv)

# Create cipher texts with modified key values
key_cipher_text_test_cases = []
for i in range(NUM_TEST_CASES):
	empty_bv = BitVector(size = 0)
	test_case_bv_fp = BitVector(filename = input_filename)
	new_encrypted_bv = DES_Price.des('e', test_case_bv_fp, empty_bv, modified_keys[i], sboxs)
	key_cipher_text_test_cases.append(new_encrypted_bv)
	test_case_bv_fp.close_file_object()

# (Optional) Write new cipher-text's to files for storaging

# Compare original cipher-text to modified key value cipher-text's
num_changed_bits_per_key_test = []

for i in range(NUM_TEST_CASES):
	num_changed_bits_per_key_test.append(0)

length_of_cipher_text = len(key_cipher_text_test_cases[0])
for i in range(NUM_TEST_CASES):
	for j in range(length_of_cipher_text):
		num_changed_bits_per_key_test[i] += 1 if (key_cipher_text_test_cases[i][j] != original_encrypted_bv[j]) else 0

confusion_average = 0
for item in num_changed_bits_per_key_test:
	confusion_average += item
confusion_average = confusion_average / NUM_TEST_CASES
confusion_percentage = (confusion_average / length_of_cipher_text) * 100

print("There was an average of %d bits changed from the original cipher-text when bits were changed in the key" % confusion_average)

#
# S-Box Diffusion Test: Generate a set of random s-box's, use them to aquire new cipher-text's and compare these with the original
#

print("\nProcessing s-box diffusion tests...")

# Generate random s-box's
# Note: There is a weird case where I cannot create the test case amount of sbox's unless
#		there is (1 + the test case) of sbox files generated
for i in range(NUM_TEST_CASES + 1):
	sbox_file = open("sbox_test_case" + str(i) + ".txt", 'w')
	for j in range(8):
		if (j != 0):
			sbox_file.write("\n")
		sbox_file.write("S" + str(j + 1) + ":\n\n")
		for z in range(4):
			for w in range(16):
				sbox_file.write(str(random.randint(0, 15)) + " ")
			sbox_file.write("\n")

random_sboxs = []
for i in range(NUM_TEST_CASES + 1):
	# Wierd case where last sbox will not be generated
	try:
		sbox = DES_Price.assemble_sboxes("sbox_test_case" + str(i) + ".txt")
		random_sboxs.append(sbox)
	except: 
		pass					
	
	if (i == (NUM_TEST_CASES)):
		random_sboxs.pop()

# Create cipher texts with modified sbox's
sbox_cipher_text_test_cases = []
for i in range(NUM_TEST_CASES):
	empty_bv = BitVector(size = 0)
	test_case_bv_fp = BitVector(filename = input_filename)
	new_encrypted_bv = DES_Price.des('e', test_case_bv_fp, empty_bv, nkey, random_sboxs[i])
	sbox_cipher_text_test_cases.append(new_encrypted_bv)
	test_case_bv_fp.close_file_object()

# (Optional) Write new cipher-text's to files for storaging

num_changed_bits_per_sbox_test = []

for i in range(NUM_TEST_CASES):
	num_changed_bits_per_sbox_test.append(0)

length_of_cipher_text = len(sbox_cipher_text_test_cases[0])
for i in range(NUM_TEST_CASES):
	for j in range(length_of_cipher_text):
		num_changed_bits_per_sbox_test[i] += 1 if (sbox_cipher_text_test_cases[i][j] != original_encrypted_bv[j]) else 0

sbox_diffusion_average = 0
for item in num_changed_bits_per_sbox_test:
	sbox_diffusion_average += item
sbox_diffusion_average = sbox_diffusion_average / NUM_TEST_CASES
sbox_diffusion_percentage = (sbox_diffusion_average / length_of_cipher_text) * 100

print("There was an average of %d bits changed from the original cipher-text when random s-box's were generated" % sbox_diffusion_average)

#
# All tests complete
#

print("\nAll tests have been completed!\n")












