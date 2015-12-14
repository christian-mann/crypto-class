from library import string_to_integer, integer_to_string
from fractions import gcd
import binascii

import Pyro4

#SERVER = "127.0.0.1"
SERVER = "10.10.200.42"

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
        
def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

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
    
    # Use the oracle to factor the given public modulus, reconstruct the private key, and decrypt the message. Use the fact that the gcd (greatest common divisor) function is very quick to compute. 
    
    # We know that the oracle is choosing two primes from a set. So, let's grab two public moduli, and check for the GCD between them. If it's something other than 1, we've recovered one of the primes.
    
    while True:
        new_public = proxy.gen_publickey()
        
        commonFactor = gcd(base_public.N(), new_public.N())
        if commonFactor != 1:
            print("Comparing base public key to new oracle key...")
            print("N1:{0} E1:{1}\nN2:{2} E2:{3}\n".format(base_public.N(), base_public.E(), new_public.N(), new_public.E()))
            print("Possible common factor: {0}\n".format(commonFactor))
            break
            
    # Now divide the target public modulus by our common factor to recover the other prime.
    
    e = base_public.E()
    n = base_public.N()
    p = commonFactor
    
    q = n / p
    
    print("Recovered P: {0}, Q: {1}".format(p, q))
    
    # Calculate the Euler totient
    totient = (p - 1) * (q - 1)
    
    # Verify gcd(e, totient) == 1
    if gcd(e, totient) != 1:
        print("Error")
    
    # Now we can compute d = e^(-1)mod ((p-1)(q-1))
    d = modinv(e, totient)
    print("Recovered private key: {0}".format(d))
    
    # Now decrypt!
    cText = string_to_integer(base_ciphertext)
    print("Decrypting ciphertext: {0}".format(cText))
    
    # m = c^(d) mod n
    m = pow(cText, d, n)
    print(m)
    m = integer_to_string(m)
    print(m)
    print("Decrypted message... {0}".format(binascii.hexlify(bytearray(m))))
