
import socket
import base64

from library import bytes_to_text

HOST = '10.10.200.42'
PORT = 5003

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

if __name__ == '__main__':
    proxy = OracleProxy(HOST, PORT)
    print proxy.process("Hello, World!").encode('hex')
