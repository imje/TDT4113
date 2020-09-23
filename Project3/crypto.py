import crypto_utils as cu
from math import gcd
import random

class Cipher:
    def __init__(self):
        self.legal_alphabet = [chr(i) for i in range(32,127)]
        self.alphabet_size = 95

    def encode(self, tekst, key):
        pass

    def decode(self, tekst, key):
        pass

    def verify(self, text, key):
        return text == self.decode(self.encode(text, key), key)

    def generate_keys(self):
        pass



class Caesar(Cipher):
    def __init__(self):
        Cipher.__init__(self)

    def encode(self, tekst, key):
        encoded_str = ''
        for char in tekst:
            encoded_str += self.legal_alphabet[(((self.legal_alphabet.index(char) + key) % self.alphabet_size))]
        return encoded_str

    def decode(self, tekst, key):
        new_key = (self.alphabet_size-key) % self.alphabet_size
        return self.encode(tekst, new_key)



class Multiplicative(Cipher):

    def __init__(self):
        Cipher.__init__(self)

    def encode(self, tekst, key):
        encoded_str = ''
        for char in tekst:
            encoded_str += self.legal_alphabet[(((self.legal_alphabet.index(char) * key) % self.alphabet_size))]
        return encoded_str

    def decode(self, tekst, key):
        new_key = cu.modular_inverse(key,self.alphabet_size)
        return self.encode(tekst, new_key)



class Affine(Cipher):
    def __init__(self):
        Cipher.__init__(self)


    def encode(self, tekst, key): #her er key en tuple
        multi_str = ''
        encoded_str = ''
        for char in tekst:
            multi_str += self.legal_alphabet[(((self.legal_alphabet.index(char) * key[0]) % self.alphabet_size))]
        for chr in multi_str:
            encoded_str += self.legal_alphabet[(((self.legal_alphabet.index(chr) + key[1]) % self.alphabet_size))]
        return encoded_str


    def decode(self, tekst, key):
        caesar_str = ''
        decoded_str = ''
        m2 = cu.modular_inverse(key[0], self.alphabet_size)
        a2 = self.alphabet_size - key[1]
        for chr in tekst:
            caesar_str += self.legal_alphabet[(((self.legal_alphabet.index(chr) + a2) % self.alphabet_size))]
        for char in caesar_str:
            decoded_str += self.legal_alphabet[(((self.legal_alphabet.index(char) * m2) % self.alphabet_size))]
        return decoded_str



class Unbreakable(Cipher):
    def __init__(self):
        Cipher.__init__(self)


    def encode(self, tekst, key): #her er key et ord
        encoded_str =''
        key_index = 0
        for char in tekst:
            new_key = self.legal_alphabet.index(char) + self.legal_alphabet.index(key[key_index%len(key)])
            encoded_str += self.legal_alphabet[new_key % self.alphabet_size]
            key_index += 1
        return encoded_str


    def decode(self, tekst, key):
        new_key = ''
        for char in key:
            new_key += self.legal_alphabet[(self.alphabet_size - self.legal_alphabet.index(char)) % self.alphabet_size]
        return self.encode(tekst,new_key)



class RSA(Cipher):

    def __init__(self):
        Cipher.__init__(self)

    def encode(self, tekst, key):
        encoded_list = []
        n = key[0]
        e = key[1]
        numbers = cu.blocks_from_text(tekst,2)
        for num in numbers:
           encoded_list.append(pow(num,int(e),int(n)))
        return encoded_list

    def decode(self, tekst, key):
        decoded_numbers = []
        n = key[0]
        d = key[1]
        for num in tekst:
            decoded_numbers.append(pow(int(num),d,n))
        return cu.text_from_blocks(decoded_numbers,8)



class Person:

    def __init__(self,key,cipher):
        self.key = key
        self.cipher = cipher

    def set_key(self,key):
        self.key = key

    def get_key(self):
        return self.key

    def operate_cipher(self, tekst):
        pass



class Sender(Person):
    def __init__(self, key, cipher):
        Person.__init__(self,key, cipher)

    def operate_cipher(self, text):
        print("Kryptert tekst er: " + str(self.cipher.encode(text, self.key)))
        return self.cipher.encode(text, self.key)

    def send_cipher(self, recevier, text):
        if isinstance(self.cipher, RSA):
            recevier.generate_keys()
            self.key = recevier.senderKey()

        recevier.recieve_cipher(self.operate_cipher(text))



class Receiver(Person):

    def __init__(self, key, cipher):
        Person.__init__(self, key, cipher)

    def operate_cipher(self, text):
        print("Dekryptert tekst er: " + str(self.cipher.decode(text, self.key)))
        return self.cipher.decode(text, self.key)

    def recieve_cipher(self, text):
        self.operate_cipher(text)

    def senderKey(self):
        return self.sender_key


    def generate_keys(self):
        p = q = 0
        gCd = 1
        while (p == q or gCd != 1):
            p = cu.generate_random_prime(8)
            q = cu.generate_random_prime(8)
            phi = (p - 1) * (q - 1)
            e = random.randint(3, (phi - 1))
            d = cu.modular_inverse(e, phi)
            gCd = gcd(e, phi)
        n = p * q

        self.sender_key = (n, e)
        self.key = (n, d)



class Hacker(Person):

    def __init__(self, cipher):
        self.cipher = cipher
        self.english_words = []
        for line in open('english_words.txt'):
            self.english_words.append(line.rstrip('\n'))


    def find_possible_keys(self):
        if isinstance(self.cipher, Caesar) or isinstance(self.cipher, Multiplicative):
            self.match = [0] * self.cipher.alphabet_size
            return [i for i in range(self.cipher.alphabet_size)]

        elif isinstance(self.cipher, Affine):
            self.match = [0] * (self.cipher.alphabet_size)**2
            return [(j, k) for j in range(0, self.cipher.alphabet_size) for k in range(0, self.cipher.alphabet_size)]

        elif isinstance(self.cipher, Unbreakable):
            self.match = [0] * len(self.english_words)
            return self.english_words


    def decode_text(self, text):
        possible_keys = self.find_possible_keys()
        for key in possible_keys:
            decoded_str = self.cipher.decode(text, key)
            for word in decoded_str.split():
                if self.english_words.__contains__(word):
                    self.match[possible_keys.index(key)] += 1

        new_key = possible_keys[self.match.index(max(self.match))]
        return self.cipher.decode(text, new_key)


def main():


    c = Caesar()
    m = Multiplicative()
    a = Affine()
    u = Unbreakable()
    r = RSA()

    cip = input("Hvilket cipher vil du bruke?"
                   "\n c : Caesar()"
                   "\n m : Multiplicative()"
                   "\n a : affine()"
                   "\n u : Unbreakable()"
                   "\n r : RSA() "
                   "\n\n Valg: ")

    if cip == "c":
        print("\n\n Du valgte caesar\n")
        s1 = Sender(3, c)
        r1 = Receiver(3, c)
        s1.send_cipher(r1, input("Tekst du vil kryptere: "))

    if cip == "m":
        print("\n\nDu valgte multiplication\n")
        s2 = Sender(2, m)
        r2 = Receiver(2, m)
        s2.send_cipher(r2, input("Tekst du vil kryptere: "))

    if cip == "a":
        print(("\n\nDu valgte affine\n"))
        s3 = Sender((2,3), a)
        r3 = Receiver((2,3), a)
        s3.send_cipher(r3, input("Tekst du vil kryptere: "))

    if cip == "r":
        print("\n\nDu valgte RSA\n")
        s4 = Sender("RSA", r)
        r4 = Receiver("RSA", r)
        s4.send_cipher(r4, input("Tekst du vil kryptere: "))

    if cip == "u":
        print("\n\nDu valgte unbreakable\n")
        s5 = Sender("lakris", u)
        r5 = Receiver("lakris", u)
        s5.send_cipher(r5, input("Tekst du vil kryptere: "))


    #Hacker
    tekst = "Good luck"
    h = Hacker(c)
    s = Sender(45, c)
    print("Tekst aa dekryptere", tekst)
    encode = s.operate_cipher(tekst)
    hacker_dekrypt = h.decode_text(encode)
    print("Hacker dekrypterte teksten til å bli:", hacker_dekrypt)
    if hacker_dekrypt == tekst:
        print("Hackeren greide det :O")

main()
