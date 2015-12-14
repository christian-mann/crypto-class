from library import string_to_integer, integer_to_string
from librsa import gen_rsa_key, rsa_decrypt

from fractions import gcd

import Pyro4

#SERVER = "neptune.local"
SERVER = "127.0.0.1"
#SERVER = "10.10.200.42"

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:ExposedKeyGenerator@" + SERVER + ":9061")

    base_public = proxy.get_flag_publickey()
    base_ciphertext = proxy.get_encrypted_flag()
    print "Encrypted message:"
    print "N:", base_public.N()
    print "E:", base_public.E()
    print "C:", string_to_integer(base_ciphertext)
    print

    recovered_primes = set()
    moduli = set()
    base_factors = []

    while not base_factors:
        public = proxy.gen_publickey()
        n = public.N()
        if n not in moduli:
            for m in moduli:
                g = gcd(n, m)
                if g not in (1, n, m):
                    for prime in (g, n / g, m / g):
                        if prime not in recovered_primes:
                            recovered_primes.add(prime)
                            print "Recovered prime %d" % g
            moduli.add(n)

        for prime in recovered_primes:
            if base_public.N() % prime == 0:
                base_factors = [prime, base_public.N() / prime]
                print "public key factors to %d x %d" % (prime, base_public.N() / prime)

    key = gen_rsa_key(p=base_factors[0], q=base_factors[1])

    print integer_to_string(rsa_decrypt(string_to_integer(base_ciphertext), key))

    #public = proxy.gen_publickey()


    #print "New public key from the key generation server:"
    #print "N:" , public.N()
    #print "E:" , public.E()
