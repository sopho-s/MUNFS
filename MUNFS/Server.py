from . import Network
import os


def init(ip, port):
    if not os.path.exists("Permissions") or not os.path.exists("Files") or not os.path.exists("Users.csv") or not os.path.exists("Groups.csv") or not os.path.exists("Used.dat"):
        os.mkdir("Permissions")
        os.mkdir("Files")
        with open("Users.csv", "w") as f:
            f.write("username,password,userid,permissions\n")
            f.write("root,,0,3")
        with open("Groups.csv", "w") as f:
            f.write("groupid,groupname,userids,permissions")
        with open("Used.dat", "w") as f:
            f.write("0")
    server = Network.Server(ip, port)
    server.StartServer()