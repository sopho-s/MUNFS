from flask import Flask, render_template, make_response, request, url_for, flash, redirect
from MUNFS import Network

app = Flask(__name__)
app.config["SECRET_KEY"] = "df0331cefc6c2b9a5d0208a726a5d1c0fd37324feba25506"

@app.route('/', methods=["POST", "GET"])
def main():
    return render_template("index.html")
    
@app.route('/interface', methods=["POST", "GET"])
def login():
    backup = ""
    if request.method == "POST" and "delete" in request.form.keys():
        webrequest = Network.WebClient("", 0)
        webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
        returnmsg = webrequest.SendCommandBasic("remove", request.form["fullpath"], request.cookies.get("uid"))
        webrequest.EndConnection()
        backup += "/../"
    if request.method == "POST" and "share" in request.form.keys():
        webrequest = Network.WebClient("", 0)
        webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
        returnmsg = webrequest.ShareFile(request.form["fullpath"], request.cookies.get("uid"), request.form["sharee"], request.form["permissions"])
        webrequest.EndConnection()
    if request.method == "POST" and "recieveshare" in request.form.keys():
        webrequest = Network.WebClient("", 0)
        webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
        returnmsg = webrequest.SendCommandBasic("acceptshare", request.form["fullpath"], request.cookies.get("uid"), request.form["shares"])
        webrequest.EndConnection()
    if request.method == "POST" and "change" in request.form.keys():
        webrequest = Network.WebClient("", 0)
        webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
        returnmsg = webrequest.ModifyFile(request.form["fullpath"], request.cookies.get("uid"), request.form["text"])
        webrequest.EndConnection()
    if request.method == "POST" and "uid" in request.cookies and "fullpath" in request.form.keys():
        if int(request.form["type"]) == 0:
            webrequest = Network.WebClient("", 0)
            webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
            returnmsg = webrequest.SendCommandBasic("getfile", request.form["fullpath"] + backup, request.cookies.get("uid"))
            webrequest.EndConnection()
            resp = make_response(render_template("editor.html", username=request.cookies.get("username"), file=returnmsg["content"], cwd=returnmsg["cwd"]))
            resp.set_cookie("dir", returnmsg["cwd"])
            resp.set_cookie("type", request.form["type"])
            return resp
        else:
            webrequest = Network.WebClient("", 0)
            webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
            returnmsg = webrequest.SendCommandBasic("getfiles", request.form["fullpath"] + backup, request.cookies.get("uid"))
            webrequest.EndConnection()
            webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
            shares, ids = webrequest.CheckShares(request.cookies.get("uid"))
            webrequest.EndConnection()
            resp = make_response(render_template("interface.html", ids=ids, username=request.cookies.get("username"), lenshare=len(shares), shares=shares, len=len(returnmsg["content"]), files=returnmsg["content"], cwd=returnmsg["cwd"]))
            resp.set_cookie("dir", returnmsg["cwd"])
            resp.set_cookie("type", request.form["type"])
            return resp
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        logincheck = Network.WebClient("", 0)
        logincheck.EstablishConnection("127.0.0.1", 42435, "WEB")
        uid = logincheck.LogOn(username, password)
        if uid == None:
            return redirect("/")
        logincheck.EstablishConnection("127.0.0.1", 42435, "WEB")
        returnmsg = logincheck.SendCommandBasic("getfiles", "/", f"{uid}")
        logincheck.EndConnection()
        logincheck.EstablishConnection("127.0.0.1", 42435, "WEB")
        shares, ids = logincheck.CheckShares(f"{uid}")
        logincheck.EndConnection()
        resp = make_response(render_template("interface.html", ids=ids, username=username, lenshare=len(shares), shares=shares, len=len(returnmsg["content"]), files=returnmsg["content"], cwd=returnmsg["cwd"]))
        resp.set_cookie("uid", f"{uid}")
        resp.set_cookie("username", f"{username}")
        resp.set_cookie("dir", returnmsg["cwd"])
        resp.set_cookie("type", "1")
        return resp
    elif request.method == "GET" and "dir" in request.cookies  and "uid" in request.cookies:
        if int(resp.cookies["type"]) == 0:
            webrequest = Network.WebClient("", 0)
            webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
            returnmsg = webrequest.SendCommandBasic("getfile", request.cookies.get("dir") + backup, request.cookies.get("uid"))
            webrequest.EndConnection()
            resp = make_response(render_template("editor.html", username=request.cookies.get("username"), file=returnmsg["content"], cwd=returnmsg["cwd"]))
            resp.set_cookie("dir", returnmsg["cwd"])
            return resp
        else:
            webrequest = Network.WebClient("", 0)
            webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
            returnmsg = webrequest.SendCommandBasic("getfiles", request.cookies.get("dir") + backup, request.cookies.get("uid"))
            webrequest.EndConnection()
            webrequest.EstablishConnection("127.0.0.1", 42435, "WEB")
            shares, ids= webrequest.CheckShares(f"{uid}")
            webrequest.EndConnection()
            resp = make_response(render_template("interface.html", ids=ids, lenshare=len(shares), shares=shares, username=request.cookies.get("username"), len=len(returnmsg["content"]), files=returnmsg["content"], cwd=returnmsg["cwd"]))
            resp.set_cookie("dir", returnmsg["cwd"])
            return resp
