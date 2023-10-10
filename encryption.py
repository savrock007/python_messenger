import random

class encryption:

    @staticmethod
    def gen_SymKey(keysize):
        SymmetricKey = random.randrange(2**(keysize-1),(2**keysize)-1)


        return SymmetricKey

    #@staticmethod                                              First Version of symmetric encryption
    #def decrypt_sym(msg,SymKey):
    #    parts = str(msg).split()
    #    plain = ''
    #    for i in parts:
    #        plain += chr(int(int(i)/int(SymKey)))
    #    return plain

    #staticmethod
    #def encrypt_sym(msg,SymKey):
    #    msg_ord = []
    #    cipher = ''
    #    for l in msg:
    #        ord_of_letter = ord(l)
    #        msg_ord.append(ord_of_letter)
    #    for i in msg_ord:
    #        cipher += str(int(i) * int(SymKey)) + " "
    #    return cipher

#--------------Symetric Encryption----------------- Second version
    @staticmethod
    def encrypt_sym(msg, SymKey):
        msg_ord = []
        cipher = ''
        for l in msg:
            ord_of_letter = ord(l)
            msg_ord.append(ord_of_letter)
        for i in msg_ord:
            mult = str(int(i) * int(SymKey))
            xor = int(mult) ^ int(SymKey)
            cipher += str(xor) + ' '

        return cipher
    @staticmethod
    def decrypt_sym(msg, SymKey):
        parts = str(msg).split()
        plain = ''
        for i in parts:
            unxor = int(i) ^ int(SymKey)

            devided = chr(round(unxor / int(SymKey)))

            plain += devided
        return plain

#--------------Hashing algorithm--------------------
    @staticmethod
    def hash(k, m, num, salt):

        h = k * (k + 3) % m * salt         # modular hashing function
        while num >= 1:
            num -= 1
            encryption.hash(h, m, num, salt)
        return h


    @staticmethod
    def hash_string(msg, g):                     # this function takes one letter of the msg convertis in into ord and performs modular devision
                                                 # on it using ord values of a different letter as modulus in order to avalanche effect
                                                 # where if one tetter is chagned it will change the whole hash and a single letters hash only
        cipher = ''
        for i in range(len(msg)):
            letter = ord(msg[i])
            if i > 0 and i != len(msg) - 1:
                hashed_letter = encryption.hash(letter, ord(msg[i - 1]), 5, g)
                cipher += str(hashed_letter)

            elif i == 0 and len(msg) != 1:
                hashed_letter = encryption.hash(letter, ord(msg[i + 1]), 5, g)
                cipher += str(hashed_letter)

            elif i == len(msg) - 1:
                # print(ord(msg[i]))
                hashed_letter = encryption.hash(letter, ord(msg[i]) / g * 2, 5, g + 5)
                # print(hashed_letter)
                cipher += str(hashed_letter)

        return cipher


    @staticmethod
    def generate_hash(msg, num, d, key_lenght):
        if len(msg) == 2:                 #if message is to short makes it longer by appending salt to it
            msg += 'salt'

        for i in range(num):                  #encrypts msg number of times specified by 'num' every time changing  one parameter
            msg = encryption.hash_string(msg, i + d)
            msg = msg[::-2]
            d += 1
        d = 4

        while len(msg) != key_lenght:           #normalizes length by rehashing it until hash is of required length

            if len(msg) > key_lenght:           # if hash is logner than required cuts hash in half and reverses then reahshes it again
                msg = msg[::-2]
                msg = encryption.generate_hash(msg, 2, d, key_lenght)
                d -= 5
            elif len(msg) < key_lenght: #if hash is shorted then needed reverses hash and rehashes
                msg = msg[::-1]
                msg = encryption.generate_hash(msg, 2, d, key_lenght)
                d += 5
            elif len(msg) == key_lenght:
                return msg
        return msg



