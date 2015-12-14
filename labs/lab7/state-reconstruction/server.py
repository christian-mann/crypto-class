import time
import random
import Pyro4

from library import MT19937

class PredictNextGenerator:
    NUM_REQUIRED = 4
    FLAG = "sample_flag"
    def __init__(self, seed):
        self.gen = MT19937(seed)
        self.seed = seed
        self.num_correct = 0
        self.guessed_wrong = False

    def next(self):
        return self.gen.next()

    def predict_next(self, guess):
        """
        Allows user to predict the next number in sequence.
        Does pump the generator once.
        """
        actual_next = self.next()
        if guess == actual_next:
            self.num_correct += 1
            return True
        else:
            self.guessed_wrong = True
            return False

    def get_flag(self):
        if self.guessed_wrong:
            raise Exception("You incorrectly predicted the RNG. Please try again with a new one.")
        if self.num_correct >= PredictNextGenerator.NUM_REQUIRED:
            return PredictNextGenerator.FLAG
        else:
            raise Exception("You must predict the RNG output %d times to get a flag" % (PredictNextGenerator.NUM_REQUIRED))
        

class RNGGenerator:
    def __init__(self):
        pass

    def create_rng(self):
        generator = PredictNextGenerator(random.randint(0, 2**32 - 1))
        self._pyroDaemon.register(generator)
        return generator


if __name__ == '__main__':
    daemon = Pyro4.Daemon(host='neptune.local', port=9072)
    uri = daemon.register(RNGGenerator, "RNGGenerator")
    print "Ready. Object URI = ", uri
    daemon.requestLoop()
