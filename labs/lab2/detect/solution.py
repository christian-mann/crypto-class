import socket

from itertools import izip_longest

import requests
from bs4 import BeautifulSoup
import json

class Proxy:
    def __init__(self, host):
        self.host = host
        self.sess = requests.Session()
        self.num_correct = 0
        self.flag = None

    def new_challenge(self, data):
        r = self.sess.get(self.host + '/new_challenge?data=' + data.encode('hex'))
        soup = BeautifulSoup(r.text, "lxml")
        ciphertext_str = soup.find(id="ciphertext").get_text()
        ciphertext = json.loads(ciphertext_str)
        challenge_id_str = soup.find(id="challenge_id").get_text()
        challenge_id = int(challenge_id_str)

        return (ciphertext, challenge_id)
    
    def solve_challenge(self, challenge_id, guess):
        r = self.sess.get(self.host + '/solve_challenge?challenge_id=' + str(challenge_id) + '&guess=' + guess)
        soup = BeautifulSoup(r.text, "lxml")
        result_str = soup.find(id="result").get_text()
        if result_str == 'Correct!':
            result = True
        else:
            result = False
        num_correct_str = soup.find(id="num_correct").get_text()
        self.num_correct = int(num_correct_str)
        flag_elem = soup.find(id="flag")
        if flag_elem:
            self.flag = flag_elem.get_text()
        return result

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return [list(a) for a in izip_longest(fillvalue=fillvalue, *args)]

class Solver:
    def __init__(self, host):
        self.proxy = Proxy(host)

    def run(self):
        while not self.proxy.flag:
            # Put in repeating phrase
            ciph, chal_id = self.proxy.new_challenge("0123456789abcdef" * 4)

            # Break into blocks
            blocks = grouper(ciph, 16, fillvalue=0x00)
            blocks = map(tuple, blocks)

            # Look for duplicates
            if len(set(blocks)) < len(blocks):
                guess = "ECB"
            else:
                guess = "CBC"

            result = self.proxy.solve_challenge(chal_id, guess)

            if result:
                print 'Correct! %d in a row' % (self.proxy.num_correct,)
            else:
                print 'Incorrect! %d in a row' % (self.proxy.num_correct,)

        print 'FLAG: %s' % (self.proxy.flag,)
        return self.proxy.flag

if __name__ == '__main__':
    g = Solver('http://localhost:5000')
    print g.run()
