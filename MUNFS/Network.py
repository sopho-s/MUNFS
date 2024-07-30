import socket
import time
import os
import random
import threading
from .Objects import Data
from .Encryption import *
from . import Threading as threading
from . import Security
from . import FileTransfer
from . import Logging

def GetDir(user, request, directory):
    valid = True
    directorysplit = directory.split("/")
    newdir = request["content"][0].split("/")
    if directorysplit[0] == "":
        directorysplit = []
    if newdir[0] == "":
        newdir = []
    for dir in newdir:
        if dir == "..":
            if len(directorysplit) > 0:
                directorysplit.pop(len(directorysplit)-1)
            else:
                user.Send({"message":"<OK>", "content":"Invalid directory"}, True)
                valid = False    
        elif dir == "." or dir == "":
            pass
        else:
            directorysplit.append(dir)
    tempdir = "/".join(directorysplit)
    return tempdir, valid

class Connection:
    def __init__(self, connection, address, name="", key1 = 0, key2 = 0, key3 = 0, key4 = 0):
        self.connection = connection
        self.address = address
        self.name = name
        self.isbusy = False
        self.isonline = True
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3
        self.key4 = key4
    def Recieve(self, amount=1028):
        return Data(self.connection.recv(amount).decode("utf-8").encode("utf-8")).Decode()
    def RecieveAll(self):
        bytes = bytearray()
        while True:
            data = self.connection.recv(1024)
            if data == "":
                return None
            bytes.extend(data)
            if bytes[-10:] == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00":
                bytes = bytes[:-10]
                break
            elif data == "":
                return ""
        return Data(bytes.decode("utf-8").encode("utf-8")).Decode()
    def Send(self, data, withnull = False):
        self.connection.sendall(Data(data).Encode().decode("utf-8").encode("utf-8"))
        if withnull:
            self.connection.sendall(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    def EndConnection(self):
        self.connection.close()
        
class Client:
    def __init__(self, name, id):
        self.name = name
        self.connection = None
        self.id = id
    def GenerateKeyLists(self, key1, key2, key3, key4):
        key1list = []
        key1 = str(key1)
        while len(key1) > 6:
            key1list.append(int(key1[-6:]))
            key1 = key1[:-6]
        key1list.append(int(key1))
        
        key2list = []
        key2 = str(key2)
        while len(key2) > 6:
            key2list.append(int(key2[-6:]))
            key2 = key2[:-6]
        key2list.append(int(key2))
        
        key3list = []
        key3 = str(key3)
        while len(key3) > 6:
            key3list.append(int(key3[-6:]))
            key3 = key3[:-6]
        key3list.append(int(key3))
        
        key4list = []
        key4 = str(key4)
        while len(key4) > 6:
            key4list.append(int(key4[-6:]))
            key4 = key4[:-6]
        key4list.append(int(key4))
        return key1list, key2list, key3list, key4list
    def EndConnection(self):
        self.connection.EndConnection()
    def EstablishConnection(self, HOST, PORT, clienttype):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            while True:
                try:
                    s.connect((HOST, PORT))
                    break
                except:
                    time.sleep(1)
            message = {"message" : "<CONNECTED>", "name" : self.name}
            s.sendall(Data(message).Encode())
            data = ""
            while len(data) == 0:
                data = Data(s.recv(1024)).Decode()
            if data["message"] != "<WELCOME>" or data["name"]  != self.name:
                raise Exception("SERVER DID NOT REPOND CORRECTLY, INSTEAD GOT: " + data)
            e = data["keys"][0]
            n = data["keys"][1]
            key1, key2, key3, key4 = EncryptionKeyGen()
            connection = Connection(s, HOST, self.name, key1, key2, key3, key4)
            key1list, key2list, key3list, key4list = self.GenerateKeyLists(key1, key2, key3, key4)
            message = {"key1" : [EncryptRSA(keyval, e, n) for keyval in key1list], "key2" : [EncryptRSA(keyval, e, n) for keyval in key2list], "key3" : [EncryptRSA(keyval, e, n) for keyval in key3list], "key4" : [EncryptRSA(keyval, e, n) for keyval in key4list]}
            s.sendall(Data(message).Encode())
            data = connection.Recieve(1024)
            print(data)
            if data["message"] != "<VALID>":
                raise Exception("RECEIVED INCORRECT RESPONSE")
            message = {"type" : "<" + clienttype + ">"}
            connection.Send(message)
            print(clienttype + " CONNECTED")
            self.connection = connection
        except KeyboardInterrupt:
            os._exit(1)
        except ConnectionResetError:
            print("CONNECTION CLOSED")
            os._exit(1)
    def Reset(self, s):
        s.close()
        print("PERFORMING CLIENT RESET")
        os._exit(1)
    def ConnectClient(self, HOST, PORT):
        self.EstablishConnection(HOST, PORT, "CLIENT")
    def SendCommandBasic(self, command, content = ""):
        self.connection.Send({"message": "<COMMAND>", "command": command, "content": content}, True)
        msg = self.connection.RecieveAll()
        if msg["message"] == "<OK>":
            return msg["content"]
    def SendFile(self, command, content):
        self.connection.Send({"message": "<COMMAND>", "command": command, "content": content}, True)
        msg = self.connection.RecieveAll()
        if msg["message"] == "<WAITING>":
           FileTransfer.SendFileUser(content[0], self.connection, False)
        if msg["message"] == "<WAITING>":
            self.connection.Send({"message": "<DONE>"}, True)
        msg = self.connection.RecieveAll()
        if msg["message"] == "<OK>": 
            return msg["content"]
    def GetFile(self, command, content):
        self.connection.Send({"message": "<COMMAND>", "command": command, "content": content}, True)
        msg = self.connection.RecieveAll()
        if msg["message"] == "<OK>" and msg["content"] == "Continue":
            self.connection.Send({"message":"<WAITING>"}, True)
        else:
            return msg["content"]
        msg = self.connection.RecieveAll()
        if msg["type"] == 0:
            with open(msg["name"].split("/")[-1], "w") as f:
                f.write(msg["content"])
        else:
            os.mkdir(msg["name"].split("/")[-1])
        self.connection.Send({"message":"<WAITING>"}, True)
        msg = self.connection.RecieveAll()
        return "File has been sucessfully downloaded"
    def LogOn(self, username, password):
        passwordhash = Security.Hash(password)
        self.connection.Send({"message": "<LOGON>", "username": username, "passhash": passwordhash}, True)
        msg = self.connection.Recieve()
        if msg["message"] == "<OK>":
            return msg["uid"]

class Server:
    def __init__(self, HOST, PORT, COMMANDS=["help", "ls", "cat", "mkuser", "rmuser", "write", "pwd", "mkdir", "cd", "rm", "put", "get", "checkperm"]):
        self.HOST = HOST
        self.PORT = PORT
        self.userthreads = []
        self.keys = [0, 0, 0, 0]
        self.e, self.d, self.n = RSA()
        self.COMMANDS = COMMANDS
        self.userarray = Security.LoadUsers()
        self.grouparray = Security.LoadGroups()
        self.logslock = threading.Lock()
    def AddUser(self, type, connection):
        print("NEW USER CONNECTED")
        self.userthreads.append(self.UserHandler(connection))
    def StartServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.HOST, self.PORT))
                while True:
                    s.listen()
                    conn, addr = s.accept()
                    data = ""
                    while len(data) == 0:
                        data = Data(conn.recv(1024)).Decode()
                    if data["message"] == "<CONNECTED>":
                        print("CONNECTION ESTABLISHING")
                        message = {}
                        message["message"] = "<WELCOME>"
                        message["name"] = data["name"]
                        name = data["name"]
                        message["keys"] = [self.e, self.n]
                        conn.sendall(Data(message).Encode())
                        data = Data(conn.recv(1024)).Decode()
                        if data == "":
                            continue
                        key1 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key1"])]))
                        key2 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key2"])]))
                        key3 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key3"])]))
                        key4 = int("".join(["0" * (6-len(str(DecryptRSA(keyval, self.d, self.n)))) + str(DecryptRSA(keyval, self.d, self.n)) for keyval in reversed(data["key4"])]))
                        objconn = Connection(conn, addr, name, key1, key2, key3, key4)
                        objconn.Send({"message" : "<VALID>"})
                        data = objconn.Recieve(1024)
                        print(data)
                        self.AddUser(data["type"], objconn)
                    else:
                        conn.sendall(Data({"message" : "CONNECTION TERMINATED"}).Encode())
                        conn.close()  
                        print(f"CLIENT SENT BAD DATA, INSTEAD GOT {data['name']}")
            except KeyboardInterrupt:
                s.close()
    @threading.threaded
    def UserHandler(self, user):
        userclass = None
        directory = ""
        while True:
            request = user.RecieveAll()
            if request == "":
                return
            if request["message"] == "<COMMAND>":
                match request["command"]:
                    case "help":
                        if "help" in self.COMMANDS:
                            user.Send({"message":"<OK>", "content":self.COMMANDS}, True)
                            Logging.log(self.logslock, f"{userclass.username} performed {request["command"]}")
                    case "ls":
                        if "ls" in self.COMMANDS:
                            tempdir, valid = GetDir(user, request, directory)
                            tmp = os.listdir("Files/" + userclass.username + "/" + tempdir + "/")
                            content = []
                            if valid:
                                for file in tmp:
                                    if directory != "":
                                        if Security.CheckPermissions(userclass, self.grouparray, userclass.username + "/" + directory + "/" + file)[0]:
                                            if os.path.isdir("Files/" + userclass.username + "/" + directory + "/" + file):
                                                content.append("\033[94m" + file + "\033[0m") 
                                            else:
                                                content.append(file)
                                    else:
                                        if Security.CheckPermissions(userclass, self.grouparray, userclass.username + "/" + file)[0]:
                                            if os.path.isdir("Files/" + userclass.username + "/" + directory + "/" + file):
                                                content.append("\033[94m" + file + "\033[0m") 
                                            else:
                                                content.append(file)
                                user.Send({"message":"<OK>", "content":content}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username}/{tempdir}/")
                            else:
                                user.Send({"message":"<OK>", "content":"Invalid file or directory"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on an invalid directory")
                    case "cat":
                        if "cat" in self.COMMANDS:
                            tempdir, valid = GetDir(user, request, directory)
                            opendir = "Files/" + userclass.username + "/" + tempdir
                            if not valid:
                                user.Send({"message":"<OK>", "content":"Invalid file or directory"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on an invalid directory")
                            elif os.path.exists(opendir):
                                if Security.CheckPermissions(userclass, self.grouparray, userclass.username + "/" + directory + "/" + request["content"][0])[1]:
                                    with open(opendir, "r") as f:
                                        user.Send({"message":"<OK>", "content":f.read()}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username}/{tempdir}/")
                            else:
                                user.Send({"message":"<OK>", "content":"File or directory does not exist"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on a non-existant directory")
                    case "write":
                        if "write" in self.COMMANDS:
                            if request["content"][0] == "dir.perm":
                                user.Send({"message":"<OK>", "content":"You cannot name a file dir.perm"}, True)
                            else:
                                tempdir, valid = GetDir(user, request, directory)
                                writedir = "Files/" + userclass.username + "/" + tempdir
                                if not valid:
                                    user.Send({"message":"<OK>", "content":"Invalid file or directory"}, True)
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on an invalid directory")
                                elif Security.CheckPermissions(userclass, self.grouparray, userclass.username + "/" + directory + "/" + request["content"][0])[2]:
                                    with open(writedir, "w") as f:
                                        f.write(request["content"][1])
                                    Security.MakePermissions(userclass.userid, False, userclass.username + "/" + directory + "/" + request["content"][0], 7)
                                    user.Send({"message":"<OK>", "content":"File written successfully"}, True)
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username}/{tempdir}/")
                                else:
                                    user.Send({"message":"<OK>", "content":"You do not have permission to write to this file"}, True)
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username}/{tempdir}/ without correct permissions")
                    case "rmuser":
                        if "rmuser" in self.COMMANDS:
                            if userclass.permissions & 2 == 0:
                                user.Send({"message":"<OK>", "content":"You do not have the permissions to perform this"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on {request["content"][0]} without correct permissions")
                            else:
                                username = request["content"][0]
                                try:
                                    os.rmdir(f"Files/{username}")
                                except FileNotFoundError:
                                    pass
                                try:
                                    os.rmdir(f"Permissions/{username}")
                                except FileNotFoundError:
                                    pass
                                with open("Users.csv", "r") as f:
                                    lines = f.readlines()
                                with open("Users.csv", "w") as f:
                                    index = 0
                                    for line in lines:
                                        if index != 0:
                                            if line.strip("\n").split(",")[0] != f"{username}":
                                                f.write(line)
                                        else:
                                            f.write(line)
                                            index += 1
                                user.Send({"message":"<OK>", "content":"User successfully removed"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on {request["content"][0]} successfully")
                    case "mkuser":
                        if "mkuser" in self.COMMANDS:
                            username = request["content"][0]
                            if userclass.permissions & 1 == 0:
                                user.Send({"message":"<OK>", "content":"You do not have the permissions to perform this"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on {request["content"][0]} without correct permissions")
                            elif os.path.exists("Files/" + username):
                                user.Send({"message":"<OK>", "content":"User already exists"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on the existing user {request["content"][0]}")
                            else:
                                passwordhash = Security.Hash(request["content"][1])
                                with open("Used.dat", "r") as f:
                                    uids = f.read().split(",")
                                    uid = random.randint(1, 1000000000000)
                                    while uid in uids:
                                        uid = random.randint(1, 1000000000000)
                                with open("Used.dat", "a") as f:
                                    f.write(f",{uid}")
                                userstring = f"{username},{passwordhash},{uid},0"
                                self.userarray.AddUser(Security.User(username, passwordhash, uid, 0))
                                print(userstring)
                                with open("Users.csv", "a") as f:
                                    f.write("\n")
                                    f.write(userstring)
                                os.mkdir(f"Files/{username}")
                                os.mkdir(f"Permissions/{username}")
                                user.Send({"message":"<OK>", "content":"User created"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on {request["content"][0]} successfully")
                    case "pwd":
                        if "pwd" in self.COMMANDS:
                            user.Send({"message":"<OK>", "content":"/"+directory}, True)
                            Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username}/{directory}")
                    case "mkdir":
                        if "mkdir" in self.COMMANDS:
                            if request["content"][0] == "dir.perm":
                                user.Send({"message":"<OK>", "content":"You cannot name a directory dir.perm"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on a dir.perm file thus was blocked")
                            elif os.path.exists("Permissions/" + userclass.username + "/" + directory + "/" + request["content"][0]) or os.path.exists("Files/" + userclass.username + "/" + directory + "/" + request["content"][0]):
                                user.Send({"message":"<OK>", "content":"File or directory already exists"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username}/{directory}/{request["content"][0]} but the directory already existed")
                            else:
                                os.mkdir("Permissions/" + userclass.username + "/" + directory + "/" + request["content"][0])
                                os.mkdir("Files/" + userclass.username + "/" + directory + "/" + request["content"][0])
                                Security.MakePermissions(userclass.userid, False, userclass.username + "/" + directory + "/" + request["content"][0] + "/dir.perm", 7)
                                user.Send({"message":"<OK>", "content":"Directory created"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username}/{directory}/{request["content"][0]} successfully")
                    case "cd":
                        if "cd" in self.COMMANDS:
                            olddirectory = directory
                            directory, valid = GetDir(userclass, request, directory)
                            if valid:
                                if os.path.exists("Files/" + userclass.username + "/" + directory):
                                    if os.path.isdir("Files/" + userclass.username + "/" + directory):
                                        if Security.CheckPermissions(userclass, self.grouparray, userclass.username + "/" + directory)[1]:
                                            user.Send({"message":"<OK>", "content":""}, True)
                                            Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} moving to {directory}")
                                        else:
                                            Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} moving to {directory} but was blocked due to not having the correct permissions")
                                            directory = olddirectory
                                            user.Send({"message":"<OK>", "content":"You do not have permission to access this directory"}, True)
                                    else:
                                        Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} moving to {directory} but this is not a directory")
                                        directory = olddirectory
                                        user.Send({"message":"<OK>", "content":"This is not a directory"}, True)
                                else:
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} moving to {directory} but this does not exist")
                                    directory = olddirectory
                                    user.Send({"message":"<OK>", "content":"This file/directory does not exist"}, True)
                            else:
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} moving to an invalid directory thus was blocked")
                                directory = olddirectory
                                user.Send({"message":"<OK>", "content":"This file/directory is not valid"}, True)
                    case "rm":
                        if "rm" in self.COMMANDS:
                            removedir, valid = GetDir(userclass, request, directory)
                            if valid:
                                os.system(f"rm -rf Files/{userclass.username}/{removedir}")
                                os.system(f"rm -rf Permissions/{userclass.username}/{removedir}")
                                user.Send({"message":"<OK>", "content":"File/directory removed"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} removing Files/{userclass.username}/{removedir} and Permissions/{userclass.username}/{removedir}")
                            else:
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} removing an invalid directory thus was blocked")
                                directory = olddirectory
                                user.Send({"message":"<OK>", "content":"This file/directory is not valid"}, True)
                    case "put":
                        if "put" in self.COMMANDS:
                            if request["content"][0] == "dir.perm":
                                user.Send({"message":"<OK>", "content":"You cannot name a file dir.perm"}, True)
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on a dir.perm file thus was blocked")
                            else:
                                user.Send({"message":"<WAITING>"}, True)
                                msg = user.RecieveAll()
                                if Security.CheckPermissions(userclass, self.grouparray, userclass.username + "/" + directory + "/" + msg["name"].split("/")[-1])[2]:
                                    if msg["type"] == 0:
                                        with open("Files/" + userclass.username + "/" + msg["name"].split("/")[-1], "w") as f:
                                            f.write(msg["content"])
                                        Security.MakePermissions(userclass.userid, False, userclass.username + "/" + directory + "/" + msg["name"].split("/")[-1], 7)
                                    else:
                                        os.mkdir("Permissions/" + userclass.username + "/" + directory + "/" + msg["name"].split("/")[-1])
                                        Security.MakePermissions(userclass.userid, False, userclass.username + "/" + directory + "/" + msg["name"].split("/")[-1] + "/dir.perm", 7)
                                    user.Send({"message":"<WAITING>"}, True)
                                    msg = user.RecieveAll()
                                    user.Send({"message":"<OK>", "content":"File has been sucessfully written"}, True)
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username + "/" + directory + "/" + msg["name"].split("/")[-1]} successfully")
                                else:
                                    user.Send({"message":"<OK>", "content":"You do not have permission to write to this file"}, True)
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username + "/" + directory + "/" + msg["name"].split("/")[-1]} but did not have permission to do so")
                    case "get":
                        if "get" in self.COMMANDS:
                            uploaddir, valid = GetDir(userclass, request, directory)
                            if valid:
                                if os.path.exists(f"Files/{userclass.username}/{uploaddir}"):
                                    user.Send({"message":"<OK>", "content":"Continue"}, True)
                                    FileTransfer.SendFileServer(userclass, self.grouparray, uploaddir, user, False)
                                    user.Send({"message": "<DONE>"}, True)
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username + "/" + uploaddir} successfully")
                                else:
                                    Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} getting an non-existant file or directory thus was blocked")
                                    user.Send({"message":"<OK>", "content":"This file/directory does not exist"}, True)
                            else:
                                Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} getting an invalid file or directory thus was blocked")
                                user.Send({"message":"<OK>", "content":"This file/directory is not valid"}, True)
                    case "checkperm":
                        if "checkperm" in self.COMMANDS:
                            checkdir, valid = GetDir(userclass, request, directory)
                            perms = Security.CheckPermissions(userclass, self.grouparray, userclass.username + "/" + checkdir)
                            user.Send({"message":"<OK>", "content":f"Access:{perms[0]}\nRead:{perms[1]}\nWrite:{perms[2]}"}, True)
                            Logging.log(self.logslock, f"{userclass.username} performed {request["command"]} on Files/{userclass.username + "/" + checkdir} successfully")
            elif request["message"] == "<LOGON>":
                userclass = self.userarray.GetUser(request["username"], request["passhash"])
                if userclass != None:
                    user.Send({"message":"<OK>", "uid":userclass.userid})
                    Logging.log(self.logslock, f"{userclass.username} logged on successfully")
                    if not os.path.exists(f"Files/{request['username']}") or not os.path.exists(f"Permissions/{request['username']}"):                 
                        os.system(f"mkdir Permissions/{request['username']}")
                        os.system(f"mkdir Files/{request['username']}")
                else:
                    Logging.log(self.logslock, f"{userclass.username} tried logged on but with an invalid username or password")
                    user.Send({"message":"<OK>", "uid":None})
                    time.sleep(3)