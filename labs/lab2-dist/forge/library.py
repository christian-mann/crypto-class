from Crypto.Cipher import AES

import operator
import base64

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

def pkcs7(buf, n):
    """
    >>> pkcs7(map(ord, "YELLOW SUBMARINE"), 20)[-2:]
    [4, 4]
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

def strip_padding(buf):
    padding_char = buf[-1]
    if all(c == padding_char for c in buf[-padding_char:]):
        ret = buf[:-padding_char]
        return ret
    else:
        raise PaddingError("Invalid padding")

class PaddingError(Exception):
    pass

def ecb_encrypt_single(buf, key):
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    return map(ord, aes.encrypt(bytes_to_text(buf)))

def ecb_decrypt_single(buf, key):
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    ret = map(ord, aes.decrypt(bytes_to_text(buf)))
    return ret

def ecb_encrypt(buf, key):
    ciphertext = []
    blocks = chunks(buf, 16, padlast=True)
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    for block in blocks:
        ciphertext += map(ord, aes.encrypt(bytes_to_text(block)))

    return ciphertext

def ecb_decrypt(buf, key):
    plaintext = []
    blocks = chunks(buf, 16, padlast=False)
    aes = AES.new(bytes_to_text(key), AES.MODE_ECB)
    for block in blocks:
        plaintext += map(ord, aes.decrypt(bytes_to_text(block)))
    return strip_padding(plaintext)

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

def cbc_encrypt(plaintext, key, iv):
    ciphertext = []
    blocks = chunks(plaintext, 16, padlast=True)
    for block in blocks:
        xor = xor_buffers(block, iv)
        cipher = ecb_encrypt_single(xor, key)
        iv = cipher[:]
        ciphertext += cipher
    return ciphertext
