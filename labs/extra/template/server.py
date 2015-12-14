import time
import random
import Pyro4

HOST = "localhost"
PORT = 0
# Not every lab will need a port, but if you do, these are the ports you should use:
# RSAParity         9081
# Stream            9082
# MITM              9083
# SRP               9084
# CRIME             9085
# Bleichenbacher    9091
# RC4               9092
# Coppersmith       9093
# DSA               9094
# MD                9095

class LabTemplate:
    FLAG = "sample_flag"
    def __init__(self):
        pass

    def get_encrypted_flag(self):
        """
        Many labs have some amount of ciphertext that is static or a "target"

        You can either put that in a variable in client.py or as a method here.

        Advantage of doing it this way: it might be a very large piece of
        ciphertext, for instance
        """
        # return self.encrypt(FLAG)
        pass

    def perform_oracle(self):
        """
        Change the name of this function to something more meaningful e.g.
        get_last_bit_decrypted()
        get_compressed_size()

        You may need more than one oracle.
        """
        pass

    def return_object(self):
        """
        Demonstrates how to return an object from Pyro4. If you need to make
        another class or something (e.g. an RNG) then this may be useful.

        If you naively return the object, it will just return the whole object
        over the wire, or not return anything at all.
        """
        # create an object
        obj = random.SystemRandom()
        # register object with Pyro4 daemon
        self._pyroDaemon.register(obj)
        return obj


if __name__ == '__main__':
    daemon = Pyro4.Daemon(host=HOST, port=PORT)
    uri = daemon.register(LabTemplate, "LabTemplate")
    print "Ready. Object URI = ", uri
    daemon.requestLoop()
