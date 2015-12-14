
import Pyro4

SERVER = "neptune.local"
CLASSNAME = "RNGGenerator"
PORT = 9071

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:" + CLASSNAME + "@" + SERVER + ":" + str(PORT))

    rng = proxy.create_rng()

    flag = rng.guess_seed(42) # Surely this will work

    print flag or "Guess was incorrect :("
