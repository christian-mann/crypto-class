import time
import random
import sys

import Pyro4

from client import SERVER, CLASSNAME, PORT

# Feel free to define any functions you need here.

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:" + CLASSNAME + "@" + SERVER + ":" + str(PORT))

    # Put your solution here.
