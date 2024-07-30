from datetime import datetime
def Log(threadlock, logdata):
    with threadlock:
        with open("server.log", "a") as f:
            f.write(f"{datetime.now()}> {logdata}\n\n")