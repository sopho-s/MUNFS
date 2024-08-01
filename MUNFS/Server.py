from . import Network
import os


def init(ip, port):
    try:
        os.mkdir("Permissions")
    except FileExistsError:
        pass
    try:
        os.mkdir("Files")
    except FileExistsError:
        pass
    if not os.path.exists("Users.csv"):
        with open("Users.csv", "w") as f:
            f.write("username,password,userid,permissions\n")
            f.write("root,,0,3")
    if not os.path.exists("Groups.csv"):
        with open("Groups.csv", "w") as f:
            f.write("groupid,groupname,userids,permissions")
    if not os.path.exists("Used.dat"):
        with open("Used.dat", "w") as f:
            f.write("0")
    if not os.path.exists("User.share"):
        with open("User.share", "w") as f:
            f.write("owner,sharee,isgroup,isuser,file,permissions")
    server = Network.Server(ip, port)
    server.StartServer()