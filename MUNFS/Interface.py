from . import Network
from getpass import getpass
import time

def interface(client, uid):
    try:
        while True:
            request = input("> ")
            request = request.split(" ")
            match request[0]:
                case "help":
                    commands = client.SendCommandBasic("help")
                    commands.append("exit")
                    commands.append("clear")
                    for i in range(len(commands)):
                        if i % 4 == 0 and i != 0:
                            print("\n")
                        print(commands[i], end="\t\t")
                    print("\n")
                case "ls":
                    files = client.SendCommandBasic("ls")
                    for file in files:
                        print(file, end="  ")
                    print("\n")
                case "cat":
                    output = client.SendCommandBasic("cat", request[1:])
                    print(output)
                case "write":
                    eof = request[2]
                    file = ""
                    index = 0
                    while True:
                        line = input("> ")
                        if line != eof:
                            if index > 0:
                                file += "\n"
                            file += line
                            index += 1
                        else:
                            break
                    request[2] = file
                    output = client.SendCommandBasic("write", request[1:])
                    print(output)
                case "mkuser":
                    output = client.SendCommandBasic("mkuser", request[1:])
                    print(output)
                case "rmuser":
                    output = client.SendCommandBasic("rmuser", request[1:])
                    print(output)
                case "exit":
                    client.EndConnection()
                    return
                case "clear":
                    print(chr(27) + "[2J")
                    print(chr(27) + "[H")
                case "pwd":
                    output = client.SendCommandBasic("pwd", request[1:])
                    print(output)
                case "mkdir":
                    output = client.SendCommandBasic("mkdir", request[1:])
                    print(output)
                case "cd":
                    output = client.SendCommandBasic("cd", request[1:])
                    print(output)
                case "rm":
                    output = client.SendCommandBasic("rm", request[1:])
                    print(output)
                case "put":
                    output = client.SendFile("put", request[1:])
                    print(output)
                case "get":
                    output = client.GetFile("get", request[1:])
                    print(output)
                case "checkperm":
                    output = client.SendCommandBasic("checkperm", request[1:])
                    print(output)
    except KeyboardInterrupt:
        print("\nIf you wish to exit use the command exit")
        interface(client, uid)

def init(ip, port):
    client = Network.Client("nick", 1)
    client.ConnectClient(ip, port)
    uid = None
    while uid == None:
        username = input("Username: ")
        password = getpass()
        uid = client.LogOn(username, password)
        if uid == None:
            print("Username or password was incorrect")
            time.sleep(3)
    print("Use the command 'help' to see what commands you may perform on this server")
    interface(client, uid)