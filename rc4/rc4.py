# RC4 Algorithm
# By Michael Price

#
# Usage: 
#
#	rc4_cipher = RC4(<key>)
#	rc4_cipher.encrypt(<plaintext_img>)
#	rc4_cipher.decrypt(<ciphertext_img>)
#

from BitVector import *
import Image

class RC4:
	def __init__(self, key):
		self.key = key
		self.key_length = len(key)
		self.im = None

	# Reset key schedule and PRG index values
	def resetS(self):
		self.state_array = self.ksa()
		self.i = 0
		self.j = 0

	# Key schedule builder
	def ksa(self):
		temp_s = []		# Temporary state array of integers 0-255
		for i in range(256):
			temp_s.append(i)

		temp_t = []		# Temporary array for key expansion
		for i in range(256):
			temp_t.append(self.key[i % self.key_length])

		# Build the key schedule
		j = 0
		for i in range(256):
			j = (j + temp_s[i] + ord(temp_t[i])) % 256
			temp_s[i], temp_s[j] = temp_s[j], temp_s[i]

		return temp_s

	# Pseudo Random Generator
	def generate_pseudorandom_byte(self):
		i = self.i 		# For ease of coding, get current index values
		j = self.j

		i = (i + 1) % 256
		j = (j + self.state_array[i]) % 256
		# Swap elements in state array
		self.state_array[i], self.state_array[j] = self.state_array[j], self.state_array[i]
		k = (self.state_array[i] + self.state_array[j]) % 256

		self.i = i 		# Set current index values
		self.j = j

		return BitVector(intVal = self.state_array[k], size = 8)

	def encrypt(self, plaintext_img):
		# If image file has not been processed try again
		self.rc4("Encryption", plaintext_img)

	def decrypt(self, encrypted_img):
		self.rc4("Decryption", encrypted_img)

	def rc4(self, encrypt_or_decrypt, image_data):
		self.resetS()		# Reset key schedule and indexes
		out_filename = "encrypted_img.ppm" if encrypt_or_decrypt is "Encryption" else "decrypted_img.ppm"

		# Capture image data
		if (self.im == None):
			self.im = Image.open(image_data)
			self.im_width = self.im.size[0]
			self.im_height = self.im.size[1]

		print ("Processing image for %s..." % encrypt_or_decrypt)

		# Begin byte by byte processing
		for x in range(self.im_width):
			for y in range(self.im_height):
				new_pix = []
				for b in self.im.getpixel((x, y)):
					bv = BitVector(intVal = b)			# Xor plaintext byte wtih next
					e_bv = bv ^ self.generate_pseudorandom_byte()	# pseudorandom value
					new_pix.append(e_bv.int_val())
				self.im.putpixel((x, y), tuple(new_pix))
		self.im.save(out_filename, "PPM")
		
		print ("%s complete!" % encrypt_or_decrypt)