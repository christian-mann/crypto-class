
import Pyro4

SERVER = "neptune.local"

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:RSABroadcast@" + SERVER + ":9041")

    ((e, n), ciph) = proxy.get_encrypted_message()
