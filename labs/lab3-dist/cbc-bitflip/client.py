
import requests
from bs4 import BeautifulSoup
import json

HOST = '10.10.200.42'
HOST = 'localhost'
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
        soup = BeautifulSoup(r.text, "lxml")
        try:
            flag = soup.find(id='flag').get_text()
            return flag
        except AttributeError:
            print r.text
            raise Exception("Sorry, you must be admin for get_flag() to work")

if __name__ == '__main__':
    p = Proxy('http://%s:%d' % (HOST, PORT))
    iv, cookie = p.update_userdata("Never gonna give you up")
    print p.get_flag(iv, cookie)
