
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
        print 'result_str', result_str
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
        

class Guesser:
    def __init__(self, host):
        self.proxy = Proxy(host)

    def run(self):
        while True:
            ciphertext, challenge_id = self.proxy.new_challenge("Hello, World!")
            # Guess ECB every time
            result = self.proxy.solve_challenge(challenge_id, "ECB")

            if result:
                print 'Correct! %d in a row' % (self.proxy.num_correct,)
            else:
                print 'Incorrect! %d in a row' % (self.proxy.num_correct,)

            if self.proxy.flag:
                print 'FLAG: %s' % (self.proxy.flag)


if __name__ == '__main__':
    g = Guesser('http://localhost:5000')
    print g.run()
