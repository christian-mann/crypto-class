import sys
import os
import string

from string import maketrans

sys.path.append('matasano')


CAESAR_KEY = 17
MONOALPHABETIC_TRANS = "incomputable"
SINGLE_XOR_KEY = 0x42
MULTIPLE_XOR_KEY = "Under Pressure"
VIGINERE_KEY = "TERMINATOR"
assert len(MULTIPLE_XOR_KEY) < 40

from challenge03 import xor_single
from challenge05 import xor_multiple
from challenge06 import transpose
from library import chunks

def caesar_encrypt(s, k):
    intab = "abcdefghijklmnopqrstuvwxyz"
    outtab = intab[k:] + intab[:k]
    assert len(intab) == len(outtab)
    trantab = maketrans(intab + intab.upper(),
            outtab + outtab.upper())
    return s.translate(trantab)

def monoalph_encrypt(s, key):
    assert all(c in string.lowercase for c in key)
    assert len(set(key)) == len(key)
    intab = string.lowercase
    outtab = key + ''.join(c for c in string.lowercase if c not in key)[::-1]
    assert len(intab) == len(outtab)

    trantab = maketrans(intab + intab.upper(),
            outtab + outtab.upper())
    return s.translate(trantab)

def viginere_encrypt(s, key):
    output = ""
    key = key.upper()
    i = 0
    for c in s:
        if c not in string.ascii_letters:
            output += c
        else:
            output += caesar_encrypt(c, ord(key[i]) - ord('A'))
            i = (i + 1) % len(key)
    return output


def encrypt_file(infile, outfile, algorithm, key):
    with open(infile, 'r') as inF:
        with open(outfile, 'w') as outF:
            s = infile.read()
            outfile.write(algorithm(s, key))

if __name__ == '__main__':
    with open("part1.plain.txt", "r") as inF:
        with open("part1.txt", "w") as outF:
            s = inF.read()
            outF.write(caesar_encrypt(s, CAESAR_KEY))

    with open("part2.plain.txt", "r") as inF:
        with open("part2.txt", "w") as outF:
            s = inF.read()
            outF.write(monoalph_encrypt(s, MONOALPHABETIC_TRANS))

    with open("part3.plain.txt", "r") as inF:
        with open("part3.txt", "w") as outF:
            s = inF.read()
            outF.write(xor_single(s, SINGLE_XOR_KEY).encode('base64'))

    with open("part4.plain.txt", "r") as inF:
        with open("part4.txt", "w") as outF:
            s = inF.read()
            outF.write(xor_multiple(s, map(ord, MULTIPLE_XOR_KEY)).encode('base64'))

    with open("part5.plain.txt", "r") as inF:
        with open("part5.txt", "w") as outF:
            s = inF.read()
            outF.write(viginere_encrypt(s, VIGINERE_KEY))


    print caesar_encrypt("abc", 3)
