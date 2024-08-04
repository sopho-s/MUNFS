import time
import random
import math
import time
from scipy import special
from .Objects import BitArray
 
 
class Key:
    def __init__(self, public, private):
        self.public = public
        self.private = private
 
 
def listsize(nth):
    tempnum = math.e ** (-special.lambertw(-1/nth, k=1))
    return int(tempnum)

def getprimes(nth):
    if nth != 1:
        size = listsize(nth)
        posprimes = [0 for i in range(0, size)]
        posprimes[0] = 1
        primes = [2]
        count = 3
        while len(primes) < nth:
            if posprimes[count] == 0:
                primes.append(count)
                mult = 0
                while mult*count < size:
                    posprimes[mult*count] = 1
                    mult += 1
            count += 2
        return primes
    return [2]

def getnthprime(nth):
    primes = getprimes(nth)
    return primes[nth-1]

def Getpartrand():
    start = time.time()
    time.sleep(0.01)
    key = time.time() - start
    start = time.time()
    time.sleep(0.01)
    key = key * 10 ** ((time.time() - start - 0.01) * 1000)
    key = int(key * 2 ** 48) % 2 ** 48
    return key

def GenerateRandom():
    stringkey = ""
    for _ in range(10):
        stringkey += str(Getpartrand())
    keylen = len(stringkey)
    output = 0
    count = 0.7723
    for char in stringkey:
        addition = ord(char) ** count
        while addition > 2 ** 64:
            addition /= 2
        output += addition
        count += 0.7723
        if count > 128:
            count -= 128
    return int(output * keylen) % (10**12)

def GenPrimes():
    prime1 = 0
    while prime1 < 1000:
        prime1 = getnthprime(GenerateRandom() % (10 ** 5))
    prime2 = 0
    while prime2 < 1000:
        prime2 = getnthprime(GenerateRandom() % (10 ** 5))
    return prime1, prime2

def RSA():
    while True:
        try:
            prime1, prime2 = GenPrimes()
            n = prime1 * prime2
            phi = (prime1-1) * (prime2-1)
            e = 2
            while phi % e == 0:
                e += 1
            d = pow(e, -1, phi)
            return e, d, n
        except ValueError:
            pass

def EncryptRSA(data, e, n):
    return pow(data, e, n)

def DecryptRSA(data, d, n):
    return pow(data, d, n)

def EncryptionKeyGen():
    strkey = str(GenerateRandom())
    key1 = (int(strkey) + Getpartrand()) % (2 ** 128)
    strkey = str(GenerateRandom())
    key2 = (int(strkey) + Getpartrand()) % (2 ** 128)
    strkey = str(GenerateRandom()) + str(GenerateRandom()) + str(GenerateRandom()) + str(GenerateRandom()) + str(GenerateRandom())
    key4 = (int(strkey) + Getpartrand()) % (2 ** 128)
    return key1, key2, 0, key4

def Encrypt(data, key1, key2, key3, key4):
    datalist = []
    while len(data) > 16:
        datalist.append(BitArray(data[0:16], 128).String())
        data = data[16:]
    datalist.append(BitArray(data, 128).String())
    returnval = ""
    for value in datalist:
        returnval += Encrypt16(value, key1, key2, key3, key4)
    return returnval

def Encrypt16(data, key1, key2, key3, key4):
    data = list(map(str, data))
    random.seed(key1)
    swaplist = [i for i in range(16)]
    for i in range(8):
        value1 = random.choice(swaplist)
        for t in range(len(swaplist)):
            if swaplist[t] == value1:
                swaplist.pop(t)
                break
        value2 = random.choice(swaplist)
        for t in range(len(swaplist)):
            if swaplist[t] == value2:
                swaplist.pop(t)
                break
        temp = data[value1]
        data[value1] = data[value2]
        data[value2] = temp
    
    random.seed(key2)
    for i in range(4):
        shift = random.randint(0, 3)
        shifted = [0, 0, 0, 0]
        for t in range(4):
            shifted[(t + shift) % 4] = data[i * 4 + t]
        for t in range(4):
            data[i * 4 + t] = shifted[t]
            
    databits = BitArray("".join(data))
    keybits = BitArray(key4)
    databits ^= keybits
    return databits.String()

def Decrypt(data, key1, key2, key3, key4):
    datalist = []
    while len(data) > 16:
        datalist.append(BitArray(data[0:16], 128).String())
        data = data[16:]
    datalist.append(BitArray(data, 128).String())
    returnval = ""
    for value in datalist:
        temp = value
        returnval += BitArray(Decrypt16(value, key1, key2, key3, key4)).StringClean()
    return returnval

def Decrypt16(data, key1, key2, key3, key4):
    databits = BitArray(data)
    keybits = BitArray(key4)
    databits ^= keybits
    data = list(map(str, databits.String()))
    random.seed(key2)
    for i in range(4):
        shift = 4 - random.randint(0, 3)
        shifted = [0, 0, 0, 0]
        for t in range(4):
            shifted[(t + shift) % 4] = data[i * 4 + t]
        for t in range(4):
            data[i * 4 + t] = shifted[t]
    
    random.seed(key1)
    swaplist = [i for i in range(16)]
    for i in range(8):
        value1 = random.choice(swaplist)
        for t in range(len(swaplist)):
            if swaplist[t] == value1:
                swaplist.pop(t)
                break
        value2 = random.choice(swaplist)
        for t in range(len(swaplist)):
            if swaplist[t] == value2:
                swaplist.pop(t)
                break
        temp = data[value1]
        data[value1] = data[value2]
        data[value2] = temp
    return "".join(data)