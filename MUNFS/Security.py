import pandas as pd
import os

class User:
    def __init__(self, username, passwordhash, userid, permissions):
        self.username = username
        self.passwordhash = passwordhash
        self.userid = userid
        self.permissions = permissions
        
class Group:
    def __init__(self, groupid, groupname, userids):
        self.groupid = groupid
        self.groupname = groupname
        self.userids = userids
    def AddUser(self, userid):
        self.userids.append(userid)
    def RemoveUser(self, userid):
        for i in range(len(self.userids)):
            if self.userids[i] == userid:
                self.userids.pop(i)
                break
    def CheckUser(self, userid):
        for id in self.userid:
            if id == userid:
                return True
        return False

class UserArray:
    def __init__(self, users):
        self.users = users
    def GetUser(self, username, passwordhash):
        print(username)
        print(passwordhash)
        for user in self.users:
            if user.username == username:
                print(user.passwordhash)
                if user.passwordhash == passwordhash:
                    return user
        return None

class GroupArray:
    def __init__(self, groups):
        self.groups = groups
    def GetGroupID(self, groupname):
        for group in self.groups:
            if group.groupname == groupname:
                return group.groupid
        return None
    def GetAllGroups(self, user):
        groups = []
        for group in self.groups:
            if group.CheckUser(user.userid):
                groups.append(group)
        return groups

def CheckPermissions(user, groups, file):
    permissionfile = "Permissions/" + file
    permissions = pd.read_csv(permissionfile)
    access = False
    read = False
    write = False
    if groups != None:
        for group in groups.groups:
            for index, permission in permissions.iterrows():
                if permission["isgroup"]:
                    if permission["id"] == group.groupid:
                        print()
                        access = access or permission["access"]
                        read = read or permission["read"]
                        write = write or permission["write"]
    for index, permission in permissions.iterrows():
        print(permission)
        if permission["isuser"]:
            if permission["id"] == user.userid:
                access = access or permission["access"]
                read = read or permission["read"]
                write = write or permission["write"]
    return (access, read, write)
        

def LoadUsers():
    userarray = []
    users = pd.read_csv("Users.csv", keep_default_na=False).reset_index()
    for _, user in users.iterrows():
        userarray.append(User(user["username"], user["password"], user["userid"], user["permissions"]))
    return UserArray(userarray)

def LoadGroups():
    grouparray = []
    groups = pd.read_csv("Groups.csv", keep_default_na=False).reset_index()
    for _, group in groups.iterrows():
        grouparray.append(Group(group["groupid"], group["groupname"], group["userids"]))
    return GroupArray(grouparray)

def Hash(input):
    return input