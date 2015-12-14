from Crypto.Cipher import AES

import operator
import base64
import functools


def memoize(f):
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

@string_compat
def pkcs7(buf, n):
    """
    >>> pkcs7(map(ord, "YELLOW SUBMARINE"), 20)[-2:]
    [4, 4]
    >>> pkcs7("YELLOW SUBMARINE", 20)[-2:]
    '\x04\x04'
    """
    amount = n - len(buf)
    return buf + [amount] * amount

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

@string_compat
def strip_padding(buf):
    padding_char = buf[-1]
    if all(c == padding_char for c in buf[-padding_char:]):
        ret = buf[:-padding_char]
        return ret
    else:
        raise PaddingError("Invalid padding")

class PaddingError(Exception):
    pass

@string_compat
def ecb_encrypt_single(buf, key):
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    return map(ord, aes.encrypt(bytes_to_text(buf)))

@string_compat
def ecb_decrypt_single(buf, key):
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    ret = map(ord, aes.decrypt(bytes_to_text(buf)))
    return ret

@string_compat
def ecb_encrypt(buf, key):
    ciphertext = []
    blocks = chunks(buf, 16, padlast=True)
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    for block in blocks:
        ciphertext += map(ord, aes.encrypt(bytes_to_text(block)))

    return ciphertext

@string_compat
def ecb_decrypt(buf, key):
    plaintext = []
    blocks = chunks(buf, 16, padlast=False)
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    for block in blocks:
        plaintext += map(ord, aes.decrypt(bytes_to_text(block)))
    return strip_padding(plaintext)

@string_compat
def cbc_decrypt(ciphertext, key, iv):
    if len(ciphertext) % 16 != 0:
        raise ValueError("Ciphertext invalid")
    plaintext = []
    blocks = chunks(ciphertext, 16, padlast=False)
    for block in blocks:
        plain = ecb_decrypt_single(block, key)
        plain = xor_buffers(plain, iv)
        iv = block[:]
        plaintext += plain

    return strip_padding(plaintext)

@string_compat
def cbc_encrypt(plaintext, key, iv):
    ciphertext = []
    blocks = chunks(plaintext, 16, padlast=True)
    for block in blocks:
        xor = xor_buffers(block, iv)
        cipher = ecb_encrypt_single(xor, key)
        iv = cipher[:]
        ciphertext += cipher
    return ciphertext

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
