import time
import random
import sys

from library import MT19937

import Pyro4

SERVER = "neptune.local"
CLASSNAME = "RNGGenerator"
PORT = 9071

def recover_seed(output, guess_range):
    for guess in guess_range:
        if guess % 100 == 0:
            sys.stdout.write("guess: %d\r" % guess)
            sys.stdout.flush()
        mt = MT19937(guess)
        if next(mt) == output:
            print
            return guess
    return None

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:" + CLASSNAME + "@" + SERVER + ":" + str(PORT))
    gen = proxy.create_rng()

    print "Generating random number..."
    output = gen.next()
    tf = int(time.time())
    print "Recovering seed..."
    guess = recover_seed(output, xrange(tf - 1100, tf+5))
    print guess
    print gen.guess_seed(guess)
