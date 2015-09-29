
import requests
from bs4 import BeautifulSoup
import json

HOST = '10.10.200.42'
PORT = 5031

class Proxy:
    def __init__(self, host):
        self.host = host

    def update_userdata(self, userdata):
        r = requests.get(self.host + '/update_userdata?userdata=' + userdata.encode('hex'))
        soup = BeautifulSoup(r.text, "lxml")
        cookie = soup.find(id='cookie').get_text().decode('hex')
        iv = soup.find(id='iv').get_text().decode('hex')

        return iv, cookie

    def get_flag(self, iv, cookie):
        """
        This won't work unless your role is 'admin'
        """
        r = requests.get(self.host + 
                '/get_flag' + 
                '?cookie=' + cookie.encode('hex') +
                '&iv=' + iv.encode('hex')
        )
        print r.text
        soup = BeautifulSoup(r.text, "lxml")
        try:
            flag = soup.find(id='flag').get_text()
            return flag
        except AttributeError:
            raise Exception("Sorry, you must be admin for get_flag() to work")

if __name__ == '__main__':
    p = Proxy('http://%s:%d' % (HOST, PORT))

    iv, cookie = p.update_userdata("A" * 16 + ":admin<true:f<b:")
    cipher_array = map(ord, cookie)
    # flip relevant bits
    cipher_array[32 + 0] ^= 0x1
    cipher_array[32 + 6] ^= 0x1
    cipher_array[32 + 11] ^= 0x1
    cipher_array[32 + 13] ^= 0x1
    cipher_array[32 + 15] ^= 0x1
    
    better_cookie = ''.join(map(chr, cipher_array))
    print p.get_flag(iv, better_cookie)
