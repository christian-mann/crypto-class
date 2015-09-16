
import requests
from bs4 import BeautifulSoup
import json

from library import chunks, text_to_bytes, bytes_to_text
import copy
import random

HOST = '10.10.200.42'
HOST = 'localhost'
PORT = 5032

class Proxy:
    def __init__(self, host):
        self.host = host

    def encrypted_message_oracle(self):
        r = requests.get(self.host + '/get_ciphertext')
        soup = BeautifulSoup(r.text, "lxml")
        encrypted_data = soup.find(id='ciphertext').get_text().decode('hex')
        iv = soup.find(id='iv').get_text().decode('hex')

        return (encrypted_data, iv)

    def padding_oracle(self, encrypted_data, iv):
        r = requests.get(self.host + 
                '/check_padding' + 
                '?encrypted_data=' + bytes_to_text(encrypted_data).encode('hex') + 
                '&iv=' + bytes_to_text(iv).encode('hex')
        )
        soup = BeautifulSoup(r.text, "lxml")
        return soup.find(id='good_padding').get_text() == 'True'

def gen_random_array(length):
    return [random.randint(0, 255) for i in xrange(length)]

"""
Currently limited to not working on the first block.

Could be extended, since we are allowed to provide the IV.

In particular, we can screw with bytes on /that/ instead of on the previous
block of the ciphertext.
"""
def recover_nth_intermediate_byte(prox, ciphertext, iv, n, suffix):
    blocks = chunks(ciphertext, 16, padlast=False)
    if (n / 16) < 1:
        raise ValueError("Sorry, CBC recovery does not work on the first block")
    if len(suffix) + n != len(ciphertext) - 1:
        raise ValueError("Length of suffix plus n must be equal to length of ciphertext - 1")
    # get rid of all trailing blocks
    blocks = blocks[ : (n/16)+1 ]
    # get rid of useless suffix information
    amount_to_keep = len(suffix) % 16
    suffix = suffix [ : amount_to_keep ]
    
    orig_blocks = copy.deepcopy(blocks)
    # ruin the padding on the last block
    while prox.padding_oracle(sum(blocks, []), iv):
        blocks[-2] = gen_random_array(16)
    padding_char = 16 - (n % 16)
    assert len(suffix) == padding_char - 1

    target_byte = -padding_char
    # set the trailing bytes to the right padding
    for i in xrange(-1, target_byte, -1):
        blocks[-2][i] = suffix[i] ^ padding_char
    # try to force the padding_char'th last byte to padding_char
    for b in xrange(256):
        blocks[-2][target_byte] = b
        print ("%02x "*16) % tuple(blocks[-2])
        if prox.padding_oracle(sum(blocks, []), iv):
            intermediate_byte = b ^ padding_char
            plaintext_byte = intermediate_byte ^ orig_blocks[-2][target_byte]
            return intermediate_byte, plaintext_byte

def recover_message(prox, ciphertext, iv):
    suffix = []
    message = []
    for n in xrange(len(ciphertext)-1, 15, -1): # excludes 16
        intermediate, byte = recover_nth_intermediate_byte(prox, ciphertext, iv, n, suffix=suffix)
        message = [byte] + message
        suffix = [intermediate] + suffix
    return message

if __name__ == '__main__':
    p = Proxy('http://%s:%d' % (HOST, PORT))
    cipher, iv = p.encrypted_message_oracle()
    print 'cipher', cipher.encode('hex')
    print 'iv', iv.encode('hex')
    cipher = text_to_bytes(cipher)
    iv = text_to_bytes(iv)
    print bytes_to_text(recover_message(p, cipher, iv))
