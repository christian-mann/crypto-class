
import Pyro4

SERVER = "localhost"
CLASSNAME = "LabTemplate"
PORT = 0

# Use this space for functions that the client needs; functions particular to this lab.

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:" + CLASSNAME + "@" + SERVER + ":" + str(PORT))

    # Demonstrate how to use your interface here.
