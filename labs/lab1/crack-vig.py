import sys

sys.path.append('matasano')

from challenge03 import score_bytes

from challenge01 import base64_to_bytes, bytes_to_text, text_to_bytes
from challenge03 import get_best_xor
from challenge04 import max_likelihood_decode
from challenge05 import xor_multiple
from library import chunks

def transpose(l):
    return zip(*l)

def popcount(n):
    return bin(n).count("1")

def hamming_distance(buf1, buf2):
    """
    >>> hamming_distance(map(ord, "this is a test"), map(ord, "wokka wokka!!!"))
    37
    """
    if len(buf1) != len(buf2):
        raise ValueError("Buffer lengths must be equal")
    return sum(popcount(b1 ^ b2) for (b1, b2) in zip(buf1, buf2))

def get_keysize_score(buf, size):
    blocks = chunks(buf, size)
    pairs = chunks(blocks, 2)[:]
    return sum(-hamming_distance(p0, p1)*1.0/size for (p0, p1) in pairs) / len(pairs)

def get_best_keysizes(buf, num_keysizes=1):
    scores = {n: get_keysize_score(buf, n) for n in xrange(2, 40)}
    best_items = sorted(scores.keys(), key=scores.get)
    return best_items[::-1][:num_keysizes]

if __name__ == '__main__':
    import sys

    ciphertext = text_to_bytes(sys.stdin.read().strip())
    best_sizes = get_best_keysizes(ciphertext, num_keysizes=10)
    print best_sizes
    for sz in best_sizes:
        key = []
        blocks = transpose(chunks(ciphertext, sz))
        for block in blocks:
            key.append(get_best_xor(block))
        print bytes_to_text(key)
        print bytes_to_text(xor_multiple(ciphertext, key))
