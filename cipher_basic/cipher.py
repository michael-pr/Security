# Basic Vignere Cipher (Alteration: A-z, a-z)
# By Michael Price

# Notes
# A-Z : 65-90
# a-z : 97-122
# Special characters: 91-96

from __future__ import print_function

import sys
from BitVector import *

# Check for the right amount of arguments
if len(sys.argv) is not 4:
	sys.exit("Usage: python cipher.py <key.txt> <input.txt> <output.txt>")

# Declerations
UPPER_AZ_START = 65 		# ASCII decimal value of 'A'
UPPER_AZ_END = 90 			# ASCII decimal value of 'Z'
LOWER_AZ_START = 97 		# ASCII decimal value of 'a'
LOWER_AZ_END = 122 			# ASCII decimal value of 'z'
AZ_MOVE = 51				# The total size of possible movement from A-z
SPACE_DEC = 32				# The ASCII character for space (in decimal)
ALPHABET_SIZE = 26			# The number of characters in the alphabet
BTWN_DIFFERENCE = 6 		# The 6 special characters between 'Z' and 'a'

# Args: [1] key [2] input [3] output

# Read the key file and store the key
keyArr = []
with open(sys.argv[1]) as fp:
	key = [x.strip('\n') for x in fp.readlines()];
	#key = [re.sub('[^a-zA-Z0-9\n\.]', '', x) for x in fp.readLines()]
	key = ''.join(key)
keyLength = len(key)

# Read the input file and create the string to encode
content = []
with open(sys.argv[2]) as fp:
	content = [x.strip('\n') for x in fp.readlines()];
	content = ''.join(content)

cipherText = ""								# Initialize the cipher-text

# Start encoding input file
for i in range(0, len(content)):
	charOrd = ord(content[i])				# Get the decimal value of the character
	if (charOrd != SPACE_DEC):				# Skip spaces
		keyOrd = ord(key[i % keyLength])	# Loop through the key value	

		# If the key is an a-z Character take away the difference between Z-a
		if (keyOrd >= LOWER_AZ_START):
			moveVal = (keyOrd - UPPER_AZ_START - 6)
		else:
			moveVal = (keyOrd - UPPER_AZ_START)

		newOrd = charOrd + moveVal			# Get the new characters decimal value

		# Check for four cases: 
		# AZ -> AZ, AZ -> az, az -> AZ, az -> az
		# If an A-Z value stays within A-Z do nothing
		# If an A-Z value moves further than Z add the difference between Z and a
		# If an a-z value stays within a-z do nothing
		# If an a-z value moves into A-Z loop it back around

		if (charOrd <= UPPER_AZ_END) and (moveVal <= 26):
			if not (newOrd <= UPPER_AZ_END):
				newOrd += 6
		elif (charOrd <= UPPER_AZ_END) and (moveVal > 26):
			newOrd += 6
			if (newOrd > LOWER_AZ_END):
				newOrd -= (AZ_MOVE + 7)
		elif (charOrd <= LOWER_AZ_END) and (moveVal <= 26):
			if (newOrd > LOWER_AZ_END):
				newOrd -= (AZ_MOVE + 7)
		elif (charOrd <= LOWER_AZ_END) and (moveVal > 26):
			if (newOrd > LOWER_AZ_END):
				newOrd -= (AZ_MOVE + 7)
				if (newOrd > UPPER_AZ_END):
					newOrd += 6

		newChar = chr(newOrd)				# Convert the decimal value to its character form
	else:
		newChar = chr(SPACE_DEC)
	cipherText += newChar					# Append the new character to the cipher-text

# Write the cipher-text to the output file
outFile = open(sys.argv[3], 'w')
print(cipherText, file = outFile)







