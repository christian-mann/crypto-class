#!/usr/bin/env python

import SocketServer
import random

from library import base64_to_bytes, bytes_to_text, bytes_to_base64
from library import ecb_encrypt, cbc_encrypt

from Crypto.Cipher import AES

FLAG = 'd6306d11-3d36-4535-8c32-e41fec917ae4'
SECRET_DATA = map(ord, "Secret data: " + FLAG)

KEY = [30, 123, 17, 190, 167, 204, 231, 196, 214, 49, 232, 202, 7, 89, 221, 17]

def gen_random_array(length):
    return [random.randint(0, 255) for i in xrange(length)]


class Oracle(SocketServer.BaseRequestHandler):
    def __init__(self, *args):
        self.key = KEY
        SocketServer.BaseRequestHandler.__init__(self, *args)

    def recv_until(self, socket, sentinel="\n"):
        full_data = ""
        while True:
            data = socket.recv(1024)
            if not data:
                break
            full_data += data
            if full_data.endswith(sentinel):
                break
        return full_data

    def handle(self):
        plaintext = base64_to_bytes(self.recv_until(self.request, sentinel="\n"))
        ciphertext = ecb_encrypt(plaintext + SECRET_DATA, self.key)
        self.request.sendall(bytes_to_base64(ciphertext) + "\n")

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == '__main__':
    SocketServer.TCPServer.allow_reuse_address = True
    t = ThreadedTCPServer(('', 1521), Oracle)
    t.serve_forever()
