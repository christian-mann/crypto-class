
import requests
from bs4 import BeautifulSoup
import json

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
                '?encrypted_data=' + encrypted_data.encode('hex') + 
                '&iv=' + iv.encode('hex'))
        soup = BeautifulSoup(r.text, "lxml")
        return soup.find(id='good_padding').get_text() == 'True'

if __name__ == '__main__':
    p = Proxy('http://%s:%d' % (HOST, PORT))
    cipher, iv = p.encrypted_message_oracle()
    print p.padding_oracle(cipher, iv)
