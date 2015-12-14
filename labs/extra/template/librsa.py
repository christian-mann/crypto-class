import sys

import random

from library import string_to_integer, integer_to_string

def miller_rabin(n, k):
    """ true if probably prime """
    # write n-1 as 2**s * d with odd d
    s = 0
    d = n-1
    while d % 2 == 0:
        s += 1
        d /= 2
    for i in xrange(k):
        a = random.randint(2, n-2)
        x = pow(a, d, n)
        if x in (1, n-1):
            continue
        for j in xrange(s-1):
            x = pow(x, 2, n)
            if x == 1:
                return False
            if x == n-1:
                break # continue outer loop
        else:
            # did not break
            return False
        # did break
        continue
    return True

def prime_gen(bits=512, error_log=100):
    while True:
        n = random.randint(0, 2**bits-1)
        if pow(2, n-1, n) != 1:
            continue
        elif miller_rabin(n, error_log):
            return n
        else:
            continue


def egcd(a, b):
    s0 = 1
    t0 = 0
    r0 = a

    s = 0
    t = 1
    r = b

    while r:
        q = r0 / r
        r0, r = r, r0 - q*r
        s0, s = s, s0 - q*s
        t0, t = t, t0 - q*t
    return (r0, s0, t0)

def invmod(a, n):
    gcd, x, y = egcd(a, n)
    if gcd == 1:
        return x % n
    else:
        raise ValueError("%d does not have an inverse mod %d" % (a, n))

class RSAPrivateKey(object):
    def __init__(self, n, d):
        self.n = n
        self.d = d
    def N(self): return self.n
    def D(self): return self.d

class RSAPublicKey(object):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def N(self): return self.n
    def E(self): return self.e

class RSAKeyPair(object):
    def __init__(self, n, e, d):
        self.public = RSAPublicKey(n, e)
        self.private = RSAPrivateKey(n, d)
        self.n = n
        self.e = e
        self.d = d

    def N(self): return self.n
    def E(self): return self.e
    def D(self): return self.d
    def getPublic(self): return self.public
    def getPrivate(self): return self.private

    def __iter__(self):
        return iter([self.public, self.private])

def gen_rsa_key(bits=512, p=None, q=None):
    if p is None and q is None:
        p, q = prime_gen(bits=bits), prime_gen(bits=bits)
    n = p * q
    et = (p-1) * (q-1)
    e = 65537
    while e < et/2:
        try:
            d = invmod(e, et)
            return RSAKeyPair(n, e, d)
        except ValueError:
            # no inverse
            e += 2
            continue

def rsa_decrypt(ciphertext, priv_key):
    was_str = False
    if type(ciphertext) == str:
        was_str = True
        ciphertext = string_to_integer(ciphertext)
    if was_str:
        return integer_to_string(pow(ciphertext, priv_key.d, priv_key.n))
    else:
        return pow(ciphertext, priv_key.d, priv_key.n)

def rsa_encrypt(plaintext, pub_key):
    was_str = False
    if type(plaintext) == str:
        was_str = True
        plaintext = string_to_integer(plaintext)
    if was_str:
        return integer_to_string(pow(plaintext, pub_key.e, pub_key.n))
    else:
        return pow(plaintext, pub_key.e, pub_key.n)

if __name__ == '__main__':
    public, private = gen_rsa_key()
    print 'e', public.e
    print 'Type message:'
    m = sys.stdin.readline()[:-1]
    M = string_to_integer(m)

    ciph = rsa_encrypt(M, public)
    plain = rsa_decrypt(ciph, private)

    print integer_to_string(plain)
