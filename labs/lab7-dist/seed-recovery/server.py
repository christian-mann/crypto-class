import time
import random
import Pyro4

from library import MT19937

class HiddenSeedGenerator:
    MAX_GUESSES = 1
    FLAG = "sample_flag"
    def __init__(self, seed):
        self.gen = MT19937(seed)
        self.seed = seed
        self.num_guesses = 0

    def guess_seed(self, guess):
        """
        Allows only MAX_GUESSES guess. If the guess is incorrect, then destroy all
        evidence.
        """
        if self.num_guesses >= HiddenSeedGenerator.MAX_GUESSES:
            raise Exception("Too many guesses; please try again with a new generator.")
        if guess == self.seed:
            return HiddenSeedGenerator.FLAG
        else:
            self.num_guesses += 1
            return False

    def next(self):
        return self.gen.next()

class RNGGenerator:
    INIT_SLEEP_MIN = 4#0
    INIT_SLEEP_MAX = 10#00
    END_SLEEP_MIN = 4#0
    END_SLEEP_MAX = 5#00
    def __init__(self):
        pass

    def create_rng(self):
        init_sleep = random.randint(RNGGenerator.INIT_SLEEP_MIN, RNGGenerator.INIT_SLEEP_MAX)
        print "init_sleep: %d" % (init_sleep,)
        time.sleep(init_sleep)
        
        seed = int(time.time())
        print "seed: %d" % (seed,)
        generator = HiddenSeedGenerator(seed)
        self._pyroDaemon.register(generator)

        end_sleep = random.randint(RNGGenerator.END_SLEEP_MIN, RNGGenerator.END_SLEEP_MAX)
        print "end_sleep: %d" % (end_sleep,)
        time.sleep(end_sleep)

        return generator


if __name__ == '__main__':
    daemon = Pyro4.Daemon(host='neptune.local', port=9071)
    uri = daemon.register(RNGGenerator, "RNGGenerator")
    print "Ready. Object URI = ", uri
    daemon.requestLoop()
