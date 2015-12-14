"""
Feel free to use any of these library functions in your code.
"""
from Crypto.Cipher import AES

import operator
import base64
import functools


def memoize(f):
    """
    Memoizing decorator. Warning -- holds onto data points for as long as the
    function itself exists. Can cause memory leaks if not careful.
    """
    cache = {}
    kwd_mark = object()
    def newF(*args, **kwargs):
        key = tuple([
            tuple(args),
            tuple(sorted(kwargs.items()))
        ])
        if key not in cache:
            cache[key] = f(*args, **kwargs)
        return cache[key]
    return newF


"""
Converts all incoming arguments to byte arrays if they are strings.

If the very first one is a string, then convert output to string.
"""
def string_compat(f):
    def compatibleF(*args):
        new_args = []
        was_str = args and type(args[0]) is str
        for a in args:
            if type(a) is str:
                new_args.append(map(ord, a))
            else:
                new_args.append(a)
        ret = f(*new_args)
        if was_str:
            return bytes_to_text(ret)
        else:
            return ret
    return compatibleF

def base64_to_bytes(s):
    return map(ord, s.decode('base64'))

def bytes_to_base64(buf):
    return base64.b64encode(bytes_to_text(buf))

def bytes_to_text(buf):
    return ''.join(map(chr, buf))

def text_to_bytes(s):
    return map(ord, s)

def xor_buffers(*buffers):
    """
    >>> xor_buffers([1], [2])
    [3]
    >>> xor_buffers([1, 1], [2, 1])
    [3, 0]
    >>> xor_buffers([1], [1], [1])
    [1]
    """
    return [reduce(operator.xor, bbb) for bbb in zip(*buffers)]

def chunks(l, n, padlast=False):
    """
    Yield successive n-sized chunks from l.

    If padlast = True, then pads the last one with pkcs#7 padding.
    """
    ret = []
    for i in xrange(0, len(l), n):
        if i + n <= len(l):
            ret.append( l[i:i+n] )
        elif padlast:
            ret.append(pkcs7(l[i:], n))
        else:
            pass
    if len(l) % n == 0 and padlast:
        # make sure padding always gets appended
        ret.append(pkcs7([], n))
    return ret

def string_to_integer(s):
    """
    Little-endian
    """
    n = 0
    for c in s:
        n *= 256
        n += ord(c)
    return n

def integer_to_string(n):
    """
    little-endian
    """
    s = ""
    while n > 0:
        s = chr(n % 256) + s
        n /= 256
    return s

class MT19937(object):
    """
    MT19937 Mersenne Twister random number generator
    >>> seed = 100
    >>> mt = MT19937(seed)
    """
    def __init__(self, seed):
        self.index = 0
        self.MT = [0] * 624

        assert type(seed) is int
        assert seed < 2**32

        self.MT[0] = seed
        for i in xrange(1, 624):
            self.MT[i] = (0x6c078965 * (self.MT[i-1] ^ (self.MT[i-1] >> 30)) + i) % (1 << 32)

    def next(self):
        if self.index == 0:
            self.generate_numbers()

        y = self.MT[self.index]
        y = y ^ (y >> 11)
        y = y ^ ((y << 7) & 0x9d2c5680)
        y = y ^ ((y << 15) & 0xefc60000)
        y = y ^ (y >> 18)

        self.index = (self.index + 1) % 624

        assert y < 2**32
        return y

    def generate_numbers(self):
        for i in xrange(624):
            y = (self.MT[i] & 0x80000000) + (self.MT[(i+1) % 624] & 0x7fffffff)
            self.MT[i] = self.MT[(i + 397) % 624] ^ (y >> 1)
            if y % 2 != 0: # y is odd
                self.MT[i] = self.MT[i] ^ 0x9908b0df
