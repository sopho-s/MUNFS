from . import Security
import os

def SendFileServer(requestee, groups, file, connection, recursive):
    if os.path.isdir("Files/" + requestee.username + "/" + file):
        connection.Send({"message":"<DATA>", "type":1, "name":file.split("/")[-1]}, True)
        connection.RecieveAll()
        files = os.listdir()
        if recursive:
            for newfile in files:
                GetFile(requestee, groups, f"{file}/{newfile}", connection, True)
    else:
        with open("Files/" + requestee.username + "/" + file, "r") as f:
            connection.Send({"message":"<DATA>", "type":0, "name":file.split("/")[-1], "content":f.read()}, True)
        connection.RecieveAll()

def GetFile(requestee, groups, file, connection, recursive=False):
    if Security.CheckPermissions(requestee, groups, file)[1]:
        SendFileServer(requestee, groups, file, connection, recursive)

def SendFileUser(file, connection, recursive):
    if os.path.isdir(file):
        connection.Send({"message":"<DATA>", "type":1, "name":file.split("/")[-1]}, True)
        connection.RecieveAll()
        files = os.listdir()
        if recursive:
            for newfile in files:
                SendFileUser(f"{file}/{newfile}", connection, True)
    else:
        with open(file, "r") as f:
            connection.Send({"message":"<DATA>", "type":0, "name":file.split("/")[-1], "content":f.read()}, True)
        connection.RecieveAll()
