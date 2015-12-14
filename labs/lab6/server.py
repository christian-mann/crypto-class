from librsa import prime_gen, gen_rsa_key, egcd, rsa_encrypt

from library import memoize

import random
import sys

import Pyro4

@memoize
class PrimePoolKeyGen(object):
    def __init__(self, bits=1024, poolsize=100):
        sys.stdout.write("Generating prime pool...")
        sys.stdout.flush()
        self.pool = []
        while len(self.pool) < poolsize:
            self.pool.append(prime_gen(bits=bits))
            print "%d/%d" % (len(self.pool), poolsize)
        print "Done"

    def gen_rsa_key(self):
        p, q = random.sample(self.pool, 2)
        return gen_rsa_key(p=p, q=q)

    def gen_first_rsa_key(self):
        p, q = self.pool[0:2]
        return gen_rsa_key(p=p, q=q)

    def write(self, filename):
        with open(filename, 'w') as f:
            for p in self.pool:
                f.write(str(p) + "\n")

    """
    Clears original pool, reads in given pool
    Changes poolsize
    >>> ppkg = PrimePoolKeyGen(poolsize=0)
    >>> ppkg.read("pool.txt")
    """
    def read(self, filename):
        with open(filename, 'r') as f:
            self.pool = [int(l) for l in f.readlines()]

        
class ExposedKeyGenerator(object):
    def __init__(self):
        self.flag = "common_divisors_are_more_than_good"
        self.pool_keygen = PrimePoolKeyGen(poolsize=0)
        self.pool_keygen.read("primes.txt")

    def gen_publickey(self):
        public, private = self.pool_keygen.gen_rsa_key()
        self._pyroDaemon.register(public)
        return public

    def get_flag_publickey(self):
        public, private = self.pool_keygen.gen_first_rsa_key()
        self._pyroDaemon.register(public)
        return public

    def get_encrypted_flag(self):
        public, private = self.pool_keygen.gen_first_rsa_key()
        return rsa_encrypt(self.flag, public)

if __name__ == '__main__':
    daemon = Pyro4.Daemon(host='neptune.local', port=9061)
    uri = daemon.register(ExposedKeyGenerator, "ExposedKeyGenerator")
    print "Ready. Object URI = ", uri
    daemon.requestLoop()
