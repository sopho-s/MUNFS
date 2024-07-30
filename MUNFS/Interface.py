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
                    for i in range(len(commands)):
                        if i % 4 == 0 and i != 0:
                            print("\n")
                        print(commands[i], end="\t\t")
                case "ls":
                    files = client.SendCommandBasic("ls")
                    for file in files:
                        print(file, end="  ")
                case "cat":
                    output = client.SendCommandBasic("cat", request[1:])
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
            print("\n")
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