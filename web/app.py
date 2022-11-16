from requests import get as get_ip
import secrets
from flask import Flask, jsonify, render_template, request, redirect, flash, url_for, make_response
from flask.views import MethodView
from flask_simplelogin import SimpleLogin, get_username, login_required
import pymongo
from flask_cors import CORS
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import json
from datetime import datetime
import pandas as pd
import random
import docker

clientD = docker.from_env()

new_init_account = {
  'userName': "Input Username",
  'password': "Input Password",
  'role': 5,
  'allowed_container': 100,
  "csrf_token": "None",
  "email": "Input email",
}
# client = pymongo.MongoClient('14.44.101.64:27017', username="ekstrah", password="KCg@9Oi1sk#j5h")
client = pymongo.MongoClient('127.0.0.1:27018')
msgClient = client
dbUserID = client['userID']
app = Flask(__name__)
CORS(app)
db = client['web']
userCollection = db['userAccount']
projectCollection = db['project']
pub_ip = get_ip('https://api.ipify.org').text

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class containerForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


def inititialize_start_account():
    new_init_account['time-created'] = str(datetime.now())
    vl = userCollection.count_documents({'userName': "ekstrah"})
    if vl == 0:
        userCollection.insert_one(new_init_account)
    else:
        print("admin account already exist")

def check_user_account(user):
    data = userCollection.find_one({"userName": user['username'], "password": user['password']})
    if not data or data['role'] == 0:
        return False
    elif data['password'] == user['password'] and data:
        userCollection.update_one({"userName": user["username"], "password": user["password"]}, {"$set": {"csrf_token": user['csrf_token']}})
        return True
    return False

app = Flask(__name__, static_url_path='/static')
CORS(app)
app.config.from_object("settings")
inititialize_start_account()


simple_login = SimpleLogin(app, login_checker=check_user_account)



@app.route("/")
def index():
    return render_template("index_home.html", )

@app.route("/home/")
def home():
	return render_template("index.html")

@app.route("/profile/")
@login_required()
def profile_view():
    return render_template("profile.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        userName= request.form.get("username")
        email = request.form.get('email')
        password = ""
        if request.form.get('password') == request.form.get("confirm"):
            password = request.form.get('password')
        else:
            flash("Yo the password and confirm password doesn't match")
            return redirect(url_for('register'))
        
        userInit = {"userName": userName, "password": password, "role": 1, "csrf_token": "None", "email": email, "allowed_container": 0, 'time-created': str(datetime.now())}
        vl =userCollection.count_documents(userInit)
        if vl > 0:
            flash("Either user exist or username is already taken")
            return redirect(url_for('register'))
        else:
            userCollection.insert_one(userInit)
        flash('Thanks for registering')
        return redirect(url_for('simplelogin.login'))
    else:
        return render_template("register.html")

@app.context_processor
def is_admin():
    user = get_username()
    if user == None:
        return dict(is_admin= 0, counter=0)
    data = userCollection.find_one({"userName": user})
    containers = projectCollection.find()
    count = 0
    resp_body = []
    for container in containers:
        projectName = container['projectName']
        port = container['Cport']
        t_dict = {'userID': user, 'port': port, 'projectName': projectName, 'Status': 'Active'}
        resp_body.append(t_dict)
        count = count + 1
    #Getting Public MQTT Broker
    if data['role'] == 5:
        return dict(is_admin= 1, counter=count, ct_body=resp_body)
    return dict(is_admin = 0, counter=count,  ct_body=resp_body)

def be_admin(user):
    """Validator to check if user has admin role"""
    data = userCollection.find_one({"userName": user})
    if data['role'] != 5:
        return "User does not have admin role"

def be_non_free(user):
    data = userCollection.find_one({"userName": user})
    if data['role'] < 2:
        return -10
    return 10

def get_role(user):
    data = userCollection.find_one({"userName": user})
    if data['role'] == 1:
        return "Free"
    if data['role'] == 3:
        return "Premium"
    return "Admin"

@app.route("/mock/<userID>/<projectName>", strict_slashes=False, methods=["GET", "POST"])
@login_required()
def topicDisplay(userID, projectName):
    if request.method == 'GET':
        data = projectCollection.find_one({"projectName": projectName})
        port = data['Wport']
        portc = data['Cport']
        tier = data['subscription']
        modelList = data['models']
        token = data['token']
        return render_template("container.html", portc=portc, token=token, port=port, pub_ip=pub_ip, tier=tier, modelList=modelList, projectName=projectName)
    if request.method == "POST":
        projectCollection.delete_one({'projectName': projectName})
        return render_template("index_home.html")

@app.route("/viewAC/<userName>", methods=["GET","POST"])
@login_required(must=[be_admin])
def complex_view(userName):
    if request.method == "GET":
        data = userCollection.find_one({'userName': userName})
        email = data['email']
        allowed_container = data['allowed_container']
        return render_template("edit_indiv_user.html", userName=userName, email=email, allowed_container=allowed_container)
    elif request.method == "POST":
        userName = request.form.get("username")
        email = request.form.get('email')
        tier = request.form.get('tier')
        allowed_container = request.form.get('containersNum')
        userCollection.update_one({'userName': userName}, {"$set" : {"role": int(tier), "allowed_container" : int(allowed_container)}})
        return redirect(url_for('viewAC'))

@app.route("/viewAC/")
@login_required(must=[be_admin])
def viewAC():
    data = userCollection.find()
    allAccount = []
    for account in data:
        tmp = {}
        tmp['userName'] = account["userName"]
        tmp['email'] = account["email"]
        tmp['role'] = account['role']
        tmp['num_cont'] = account['allowed_container']
        tmp['time-created'] = account['time-created']
        allAccount.append(tmp)
    data = userCollection.find({"isVerified": 0})
    unVerifiedAccount = []
    for account in data:
        unVerifiedAccount.append(account["userName"])
    return render_template("edit_user.html", allAccount=allAccount, unVerifiedAccount=unVerifiedAccount)


def create_Container(ocport, webport, token):
    imageName = "ekstrah/objweb:latest"
    port_dict = {str(webport)+"/tcp" : ('0.0.0.0', webport), str(ocport)+"/udp" :('0.0.0.0', ocport)}
    commandT = str(webport) + " " + str(ocport) + " 9881 " + token
    container = clientD.containers.run(image=imageName, command=commandT, detach=True, ports=port_dict)


@app.route("/createC/", methods=["POST", "GET"])
@login_required()
def create_container():
    username = get_username()
    if request.method == 'GET':
        if be_non_free(username) < 0:
            return render_template("non_free.html")
        return render_template("createProject.html", userID=username)
    else:
        test_val = request.form
        data = test_val.to_dict()
        modelList = []
        sData = {}
        sData['projectName'] = data['projectName']
        sData['subscription'] = data['subscription']
        sData['userID'] = username
        if 'car' in data:
            modelList.append('car')
        if 'person' in data:
            modelList.append('person')
        if 'dog' in data:
            modelList.append('dog')
        if 'cat' in data:
            modelList.append('cat')
        sData['models'] = modelList
        sData['Wport'] = random.randint(10000, 20000)
        sData['Cport'] = random.randint(10000, 20000)
        sData['token'] = secrets.token_hex(nbytes=12)
        create_Container(sData['Cport'], sData['Wport'], sData['token'])
        projectCollection.insert_one(sData)
        return render_template("createProject.html", userID = username)


@app.route('/user/update', methods=['GET', 'POST'])
@login_required(must=[be_admin])
def updaet_user_account():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        tData = userCollection.update_one({'userName': data['userName']}, {"$set" : {"role": int(data['tier']), "allowed_container" : int(data['ctn_count'])}})
    return "a"

@app.route("/help")
def help():
    return redirect('https://ekstrah.notion.site/MQTT-Broker-Wiki-37f0516e51834a1590912f81cb5348ff')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
