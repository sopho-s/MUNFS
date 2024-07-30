import time
def Log(threadlock, logdata):
    with threadlock:
        with open("server.log", "a") as f:
            f.write(f"{time.gmtime()}> {logdata}\n\n")