
import Pyro4

from library import integer_to_string, string_to_integer

import operator
from collections import defaultdict
import decimal

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

def find_invpow(x,n):
    """Finds the integer component of the n'th root of x,
    an integer such that y ** n <= x < (y + 1) ** n.
    """
    high = 1
    while high ** n < x:
        high *= 2
    low = high/2
    while low < high:
        mid = (low + high) // 2
        if low < mid and mid**n < x:
            low = mid
        elif high > mid and mid**n > x:
            high = mid
        else:
            return mid
    return mid + 1

def prod(l):
    return reduce(operator.mul, l, 1)

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:RSABroadcast@10.10.200.42:9041")

    # generate 5 keys with e=5
    csd = defaultdict(list)
    nsd = defaultdict(list)

    while not any(len(csd[k]) == k for k in csd):
        print 'Generating message...',
        ((e, n), ciphertext) = proxy.get_encrypted_message()
        print 'e =', e
        csd[e].append(string_to_integer(ciphertext))
        nsd[e].append(n)

    e = [k for k in csd if len(csd[k]) == k][0]
    ns = nsd[e]
    cs = csd[e]

    ms = [
        prod(ns[j] for j in xrange(e) if j != i)
        for i in xrange(e)
    ]

    #ms = [
    #            ns[1] * ns[2],
    #    ns[0]         * ns[2],
    #    ns[0] * ns[1]
    #]

    #N = ns[0] * ns[1] * ns[2]

    N = prod(ns)

    result = sum(cs[i] * ms[i] * modinv(ms[i], ns[i]) for i in xrange(e)) % N

    print result

    P = find_invpow(result, e)

    P = decimal.Decimal(result) ** decimal.Decimal(1. / e)

    print integer_to_string(P)

