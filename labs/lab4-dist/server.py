from librsa import gen_rsa_key, rsa_encrypt, rsa_decrypt

import Pyro4

class RSABroadcast(object):
    def __init__(self):
        self.message = "rsabroadcast_message"

    def get_encrypted_message(self):
        public, private = gen_rsa_key()
        ciphertext = rsa_encrypt(self.message, public)
        return (public, ciphertext)

class RSABroadcastNo3(object):
    def __init__(self):
        self.message = "rsabroadcast_3_message"

    def get_encrypted_message(self):
        while True:
            public, private = gen_rsa_key()
            (e, n) = public
            if e != 3:
                ciphertext = rsa_encrypt(self.message, public)
                return (public, ciphertext)


if __name__ == '__main__':
    daemon = Pyro4.Daemon(host='neptune.local', port=9041)
    uri = daemon.register(RSABroadcast, "RSABroadcast")
    uri = daemon.register(RSABroadcastNo3, "RSABroadcastNo3")
    print "Ready. Object URI = ", uri
    daemon.requestLoop()
