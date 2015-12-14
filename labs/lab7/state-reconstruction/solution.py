from library import MT19937

import Pyro4

SERVER = "neptune.local"
CLASSNAME = "RNGGenerator"
PORT = 9072

class SettableMT19937(MT19937):
    def set_previous_state(self, state):
        if not isinstance(state, list) or not all(isinstance(e, int) for e in state):
            raise TypeError("State must be a list of integers")
        if len(state) != 624:
            raise ValueError("State must be 624 integers long")
        # set the MT array to the state and set index to 0
        # this will force the generator to create new elements
        self.MT = state[:]
        self.index = 0

def xor_leftshift_and_magic(x, amt, magic):
    return x ^ ((x << amt) & magic)

def un_xor_rightshift(y, amt, size=32):
    """
    y = x ^ (x >> amt)

      y ^ (y >> amt)
    = (x ^ (x >> amt)) ^ ((x ^ (x >> amt)) >> amt)
    = x ^ (x >> amt) ^ (x >> amt) ^ (x >> amt >> amt)
    = x ^ (x >> (2*amt))
    """
    if amt < 0:
        raise ValueError("Shift amounts must be positive.")
    elif amt == 0:
        raise ValueError("XOR rightshift not invertible in the case of amt=0")
    elif amt >= size:
        # if we shift by 32 bits, it's like we haven't shifted at all
        return y
    else:
        return un_xor_rightshift(y ^ (y >> amt), amt * 2, size=size)

def un_xor_leftshift_and_magic(y, amt, magic, size=32):
    """
    y = x ^ ((x << amt) & magic)

    let x_L == x << amt
    and x_R == x >> amt
    and m == magic

    note that _L distributes across all Boolean operators

    y = x ^ (x_L & m)

      y ^ ((y << 2) & m) =
    = (x ^ (x_L & m)) ^ (( (x ^ (x_L & m))_L) & m)
    = x ^ (x_L m) ^ ((x_L ^ (x_L m)_L) m)
    = x ^ (x_L m) ^ ((x_L ^ (x_L_L m_L)) m)
        because (a ^ b)c == ac ^ bc, (distributing the last m)
    = x ^ (x_L m) ^ ((x_L m) ^ (x_L_L m_L m))
    = x ^ (x_L m) ^ (x_L m) ^ (x_L_L m_L m)
    = x ^ (x_L_L (m_L m))
    = x ^ ((x << 2*amt) & (magic & (magic << amt)))
    = x ^ ((x << amt') & magic')

    So we can reduce the problem. Base case happens when either:
    1. magic = 0, or
    2. amt > size

    In each of those cases, x = y.
    """
    if amt < 0:
        raise ValueError("Shift amounts must be positive.")
    elif amt == 0:
        raise ValueError("XOR leftshift and magic not invertible in the case of amt=0")
    elif magic == 0:
        # if magic is zero, then we xored with zero and nothing happened
        # this serves as a base case
        return y
    elif amt >= size:
        # we shifted all the way out, so we xored with zero
        # another base case
        return y
    else:
        return un_xor_leftshift_and_magic(xor_leftshift_and_magic(y, amt, magic), amt * 2, (magic & (magic << amt)), size=size)

def temper(y):
    y = y ^ (y >> 11)
    y = y ^ ((y << 7) & 0x9d2c5680)
    y = y ^ ((y << 15) & 0xefc60000)
    y = y ^ (y >> 18)
    return y

def untemper(n):
    n = un_xor_rightshift(n, 18)
    n = un_xor_leftshift_and_magic(n, 15, 0xefc60000)
    n = un_xor_leftshift_and_magic(n, 7, 0x9d2c5680)
    n = un_xor_rightshift(n, 11)
    return n

def clone(mt):
    """
    Clones an MT19937 PRNG using only its output.

    If the output is important to save, this method could be modified to take
    in a list of outputs instead of the generator itself.
    """
    state = []
    for i in xrange(624):
        out = mt.next()
        state.append(untemper(out))
    new_gen = SettableMT19937(0)
    new_gen.set_previous_state(state)
    return new_gen

def clone_from_outputs(outputs):
    state = []
    for out in outputs:
        state.append(untemper(out))
    new_gen = SettableMT19937(0)
    new_gen.set_previous_state(state)
    return new_gen

if __name__ == '__main__':
    import time

    proxy = Pyro4.Proxy("PYRO:" + CLASSNAME + "@" + SERVER + ":" + str(PORT))
    rng = proxy.create_rng()

    rng2 = clone(rng)

    for _ in xrange(10):
        print rng.next(), rng2.next()

    for i in xrange(4):
        rng.predict_next(rng2.next())

    print rng.get_flag()

