import json

class Data:
    def __init__(self, data = None):
        self.data = data
    def Stringify(self):
        if type(self.data) != str:
            self.data = json.dumps(self.data)
    def JSONify(self):
        if len(self.data) == 0:
            self.data = {"content": "test"}
        if type(self.data) != dict:
            self.data = json.loads(self.data)
    def Encode(self):
        self.Stringify()
        return self.data.encode("utf-8")
    def Decode(self):
        self.data = self.data.decode("utf-8")
        self.JSONify()
        return self.data

class BitArray:
    def __init__(self, data, length = 128):
        if type(data) == int:
            self.data = bin(data)
            self.data = self.data[2:]
            self.data = "0" * (length - len(self.data)) + self.data
        else:
            self.data = ""
            for let in data:
                temp = bin(ord(let))[2:]
                self.data += "0" * (8 - len(temp)) + temp
            self.data = "0" * (length - len(self.data)) + self.data
        self.length = length
    def __getitem__(self, bit):
        return int(self.data[bit])
    def __str__(self):
        return self.data
    def __ixor__(self, data):
        returnval = [0 for i in range(self.length)]
        for i in range(128):
            if (int(data.data[i]) + int(self.data[i])) % 2 == 1:
                returnval[i] = 1
        self.data = returnval
        return self
    def append(self, data):
        self.data += data.data
        self.length += data.length
    def String(self):
        returnval = ""
        for i in range(0, self.length, 8):
            returnval += chr(int("0b" + "".join([str(val) for val in self.data[i:i+8]]), 2))
        return returnval
    def StringClean(self):
        returnval = ""
        for i in range(0, self.length, 8):
            val = chr(int("0b" + "".join([str(val) for val in self.data[i:i+8]]), 2))
            if val != chr(0):
                returnval += val
        return returnval