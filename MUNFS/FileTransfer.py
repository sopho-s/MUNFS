from . import Security
import os
import base64
from . import Logging

def SendFileServer(requestee, groups, file, connection, startdirlength, recursive):
    if os.path.isdir("Files/" + requestee.username + "/" + file):
        connection.Send({"message":"<DATA>", "type":1, "name":"/".join(file.split("/")[startdirlength-1:])}, True)
        connection.RecieveAll()
        files = os.listdir(file)
        if recursive:
            for newfile in files:
                GetFile(requestee, groups, f"{file}/{newfile}", connection, startdirlength, True)
    else:
        try:
            with open("Files/" + requestee.username + "/" + file, "r") as f:
                connection.Send({"message":"<DATA>", "type":0, "name":"/".join(file.split("/")[startdirlength-1:]), "content":f.read()}, True)
        except UnicodeDecodeError:
            with open(file, "rb") as f:
                connection.Send({"message":"<DATA>", "type":2, "name":"/".join(file.split("/")[startdirlength-1:]), "content":base64.b64encode(f.read()).decode("ascii")}, True)
        connection.RecieveAll()
        
def RecieveFileServer(userclass, grouparray, directory, msg, connection, failed, logslock, request):
    if Security.CheckPermissions(userclass, grouparray, userclass.username + "/" + directory + "/" + msg["name"]):
        if msg["type"] == 0:
            with open("Files/" + userclass.username + "/" + msg["name"], "w") as f:
                f.write(msg["content"])
            Security.MakePermissions(userclass.userid, False, userclass.username + "/" + directory + "/" + msg["name"], 7)
        elif msg["type"] == 2:
            with open("Files/" + userclass.username + "/" + msg["name"], "wb") as f:
                f.write(base64.b64decode(msg["content"]))
            Security.MakePermissions(userclass.userid, False, userclass.username + "/" + directory + "/" + msg["name"], 7)
        else:
            try:
                os.mkdir("Files/" + userclass.username + "/" + directory + "/" + msg["name"])
            except FileExistsError:
                pass
            try:
                os.mkdir("Permissions/" + userclass.username + "/" + directory + "/" + msg["name"])
            except FileExistsError:
                pass
            Security.MakePermissions(userclass.userid, False, userclass.username + "/" + directory + "/" + msg["name"] + "/dir.perm", 7)
        connection.Send({"message":"<WAITING>"}, True)
        Logging.Log(logslock, f"{userclass.username} performed " + request["command"] + f" on Files/{userclass.username}/{directory}/" + msg["name"] + f" successfully")
        return connection.RecieveAll(), failed
    else:
        connection.Send({"message":"<OK>", "content":"You do not have permission to write to this file"}, True)
        failed = True
        Logging.Log(logslock, f"{userclass.username} performed " + request["command"] + f" on Files/{userclass.username}/{directory}/" + msg["name"] + f" but did not have permission to do so")
    return msg, failed

def RecieveFileUser(msg, connection):
    name = msg["name"]
    print(f"Downloaded {name}")
    if msg["type"] == 0:
        with open(msg["name"], "w") as f:
            f.write(msg["content"])
    elif msg["type"] == 2:
        with open(msg["name"], "wb") as f:
            f.write(base64.b64decode(msg["content"]))
    else:
        try:
            os.mkdir(msg["name"])
        except FileExistsError:
            pass
    connection.Send({"message":"<WAITING>"}, True)
    return connection.RecieveAll()

def GetFile(requestee, groups, file, connection, startdirlength, recursive=False):
    if Security.CheckPermissions(requestee, groups, file)[1]:
        SendFileServer(requestee, groups, file, connection, startdirlength, recursive)

def SendFileUser(file, connection, startdirlength, recursive):
    print(f"Uploading {file}")
    if os.path.isdir(file):
        connection.Send({"message":"<DATA>", "type":1, "name":"/".join(file.split("/")[startdirlength-1:])}, True)
        connection.RecieveAll()
        files = os.listdir(file)
        if recursive:
            for newfile in files:
                SendFileUser(f"{file}/{newfile}", connection, startdirlength, True)
    else:
        try:
            with open(file, "r") as f:
                connection.Send({"message":"<DATA>", "type":0, "name":"/".join(file.split("/")[startdirlength-1:]), "content":f.read()}, True)
        except UnicodeDecodeError:
            with open(file, "rb") as f:
                connection.Send({"message":"<DATA>", "type":2, "name":"/".join(file.split("/")[startdirlength-1:]), "content":base64.b64encode(f.read()).decode("ascii")}, True)
        connection.RecieveAll()

def Share(file, owner, sharee, isuser, isgroup, permissions):
    with open("User.share", "a") as f:
        f.write("\n")
        f.write(f"{owner.userid},{sharee},{isgroup},{isuser},{file},{permissions}")
        AddPermissions(file, owner, sharee, isuser, isgroup, permissions, True)


def AddPermissions(file, owner, sharee, isuser, isgroup, permissions, recursive=False):
    if os.path.isdir("Files/" + owner.username + "/" + file):
        Security.AddPermissions(sharee, isgroup, owner.username + "/" + file + "/dir.perm", permissions)
        files = os.listdir(file)
        if recursive:
            for newfile in files:
                AddPermissions(f"{file}/{newfile}", owner, sharee, isuser, isgroup, permissions, recursive)
    else:
        print(file)
        Security.AddPermissions(sharee, isgroup, owner.username + "/" + file, permissions)