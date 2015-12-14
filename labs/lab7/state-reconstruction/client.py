
import Pyro4

SERVER = "neptune.local"
CLASSNAME = "RNGGenerator"
PORT = 9072

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:" + CLASSNAME + "@" + SERVER + ":" + str(PORT))

    rng = proxy.create_rng()

    rng.predict_next(420)
    rng.predict_next(8675309)
    rng.predict_next(65535)
    rng.predict_next(1234567890)
    rng.predict_next(5555555)

    flag = rng.get_flag()

    print flag or "Guesses were incorrect :("
