
import requests
from bs4 import BeautifulSoup
import json

class Proxy:
    def __init__(self, host):
        self.host = host

    def new_profile(self, email):
        r = requests.get(self.host + '/new_profile?email=' + email)
        soup = BeautifulSoup(r.text, "lxml")
        profile = soup.find(id='plain_profile').get_text()
        enc_profile = soup.find(id='encrypted_profile').get_text()

        # You might want this:
        return (profile, enc_profile)
        # Or this:
        #return (profile, enc_profile.decode('hex'))

    def decrypt_to_dict(self, enc_profile):
        r = requests.get(self.host + '/view_profile?encrypted_profile=' + enc_profile)
        soup = BeautifulSoup(r.text, "lxml")
        profile_dict_str = soup.find(id='profile_dict').get_text()
        profile_dict = json.loads(profile_dict_str)
        return profile_dict

if __name__ == '__main__':
    p = Proxy('http://localhost:8000')
    profile, enc_profile = p.new_profile('foobar@gmail.com')
    print p.decrypt_to_dict(enc_profile)
