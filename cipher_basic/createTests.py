from __future__ import print_function

upperAZ = []
for i in range(65, 91):
	upperAZ.append(i)

lowerAZ = []
for i in range(97, 123):
	lowerAZ.append(i)

testString = ""
for i in range(0, 26):
	for j in range(0, 26):
		testString += chr(upperAZ[i])
	testString += " "
	for j in range(0, 26):
		testString += chr(upperAZ[i])
	testString += " "

for i in range(0, 26):
	for j in range(0, 26):
		testString += chr(lowerAZ[i])
	testString += " "
	for j in range(0, 26):
		testString += chr(lowerAZ[i])
	testString += " "

testKey = ""
for i in range(0, 26):
	testKey += chr(upperAZ[i])
testKey += 'a'
for i in range(0,26):
	testKey += chr(lowerAZ[i])
testKey += 'a'

contentFile = open("testall.txt", 'w')
print(testString, file = contentFile)
contentFile.close()

keyFile = open("keyall.txt", 'w')
print(testKey, file = keyFile)
keyFile.close()


#keyFile = open("keyall.txt", 'w')

