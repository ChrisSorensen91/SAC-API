import logging
from flask import Flask, render_template, request
from flask.signals import template_rendered
import json
import SAC as h

# Define APP.
app = Flask(__name__, template_folder='./templates')

# BEGIN APP:
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)

#logging.basicConfig(level=logging.debug)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create_user', methods=["GET", "POST"])
def nav_create_user():
    return render_template('create_user.html')

@app.route('/post_create_user/', methods=["GET", "POST"])
def createUser():
    h.UserManagement.createUser("CSO","Sørensen","cso@innologic.dk","Christian", managerId="IL0001")
    return render_template('create_user_req.html', user_id="CSO")

@app.route('/assign_roles', methods=["GET", "POST"])
def nav_assign_roles():
    userList = []
    userList = h.UserManagement.getUsers(returnType='custom', selectEntities=['Id'])
    groupList = {}
    groupList = h.UserManagement.getGroups(returnType='custom', selectEntities=['id', 'displayName', 'roles'])
    rolesList = {}
    rolesList = get_roles()

    return render_template('assign_roles.html', userList=userList, groupList=groupList, rolesList=rolesList)
    
def get_roles():
    with open(r"C:\Users\cso\SAC\data\roles.json") as f:
        data = json.load(f)
    return data["Roles"]

@app.route('/delete_user') #<-- TODO
def nav_delete_users():
    return render_template('delete_user.html')  # <>

@app.route('/post_assign_priv/', methods=["GET", "POST"])
def putAssign():
    h.UserManagement.assignPrivileges("CSO", ["PROFILE:sap.epm:Viewer, PROFILE:t.S:cso_test"])
    return render_template('assign_roles_req.html', roles="PROFILE:sap.epm:Viewer, PROFILE:t.S:cso_test", user_id="CSO")


def home():
    return render_template('home.html')
#

def nav_create_user():
    return render_template('create_user.html')

def nav_delete_users():
    return render_template('delete_user.html')
