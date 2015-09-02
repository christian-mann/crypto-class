
import socket
import base64
import time

from library import bytes_to_text

class OracleProxy:
    def __init__(self, host, port):
        self.host = host
        self.port = port

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

    def process(self, data):
        if isinstance(data, list):
            data = bytes_to_text(data)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))

        sock.send(base64.b64encode(data) + "\n")
        ciphertext = self.recv_until(sock, sentinel="\n")
        sock.close()
        return base64.b64decode(ciphertext)

class Solver:
    def __init__(self, host, port):
        self.proxy = OracleProxy(host, port)
        self.first_bytes = []
        self.block_size = 16

    def recover_byte(self):
        block_size = self.block_size

        byte_number = len(self.first_bytes)
        block_number = byte_number / block_size
        block_offset = (block_size - 1) - (byte_number % block_size)
        relevant_slice = slice(block_number * block_size, (block_number + 1) * block_size)

        nonce = [0] * (block_offset)
        cipher = self.proxy.process(nonce)[relevant_slice]
        try:
            for b in xrange(256):
                cipher2 = self.proxy.process(nonce + self.first_bytes + [b])[relevant_slice]
                if cipher == cipher2:
                    return b
        finally:
            pass

    def recover_bytes(self):
        for i in xrange(1000):
            byte = self.recover_byte()
            if byte is None:
                break
            else:
                self.first_bytes.append(byte)
                print bytes_to_text(self.first_bytes)
                time.sleep(0.1) # For effect and to not hammer the server

if __name__ == '__main__':
    solver = Solver('localhost', 1521)
    print solver.recover_bytes()
