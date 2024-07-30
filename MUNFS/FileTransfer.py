from . import Security
import os

def SendFile(requestee, groups, permissions, file, connection, recursive):
    if os.path.isdir(file):
        connection.Send({"type":1, "name":file[5:], "permissions":permissions})
        files = os.listdir()
        if recursive:
            for newfile in files:
                GetFile(requestee, groups, f"{file}/{newfile}", connection, True)
    else:
        with open(file, "r") as f:
            connection.Send({"type":0, "name":file[5:], "content":f.read(), "permissions":permissions})

def GetFile(requestee, groups, file, connection, recursive=False):
    if Security.CheckPermissions(requestee, groups, file)[1]:
        files = "Files/" + requestee.username + "/" + file

def UploadFile(requestee, groups, file, connection, recursive=False):
    if Security.CheckPermissions(requestee, groups, file)[1]:
        files = "Files/" + requestee.username + "/" + file
    