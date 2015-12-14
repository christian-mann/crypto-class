from library import string_to_integer

import Pyro4

#SERVER = "127.0.0.1"
SERVER = "10.10.200.42"

if __name__ == '__main__':
    proxy = Pyro4.Proxy("PYRO:ExposedKeyGenerator@" + SERVER + ":9061")

    base_public = proxy.get_flag_publickey()
    base_ciphertext = proxy.get_encrypted_flag()
    print "Encrypted message:"
    print "N:", base_public.N()
    print "E:", base_public.E()
    print "C:", string_to_integer(base_ciphertext)
    print

    public = proxy.gen_publickey()


    print "New public key from the key generation server:"
    print "N:" , public.N()
    print "E:" , public.E()
