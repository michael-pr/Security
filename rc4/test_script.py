# Testing script

from hw05 import *
from rc4 import *


rc4_cipher = RC4("thisisateststrin")
rc4_cipher.encrypt("tiger2.ppm")
rc4_cipher.decrypt("encrypted_image.ppm")


#rc4 = RC4_test("thisisateststrin")
#rc4.encrypt("tiger2.ppm")