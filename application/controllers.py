from flask import current_app as app, redirect, url_for 
from flask import request
from flask import render_template
from .models import Users, FilesUploaded
from .database import db 
import os
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from main import bcrypt
import os
import zipfile
import shutil
import time
import subprocess
import socket 

# from flask import current_app as app
# userPortNo = 5001
print("inside controllers")

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

@loginManager.user_loader
def load_user(userIdNo):
    return Users.query.filter_by(userIdNo=userIdNo).first()

@app.route('/')
def home():
    print("hello world")
    return "hello world"


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        userID = request.form.get('userID')
        userPassword = request.form.get('userPassword')
        # newUser = Users(userIdNo = 0, userPassword = userPassword, userId = userID, companyName = "OSCORP", dataFolder ="klll")
        # db.session.add(newUser)
        # db.session.commit()
        print(userID)
        print(userPassword)
        user = Users.query.filter_by(userId=userID).first()
        print(user)
        if user:
            if user.userPassword == userPassword :
                print("Password is correct")
                login_user(user)
                return redirect(url_for('dashboard'))
        else :
            return render_template('login.html')
        print(userID, userPassword)
        return redirect(url_for('dashboard'))
    

def createFolder(userID):
    # os.chdir('')
    abs_path = os.path.join(os.path.abspath('./static'), userID)
    if os.path.exists(abs_path):
        print("exists", abs_path)
    else :
        try:
            os.makedirs(abs_path)
            print("creating", abs_path)
            sub_folder_data = os.path.join(abs_path,"data")
            sub_folder_domain = os.path.join(abs_path,"domain")
            sub_folder_models = os.path.join(abs_path,"models")
            sub_folder_uploaded_files = os.path.join(abs_path,"uploaded_files")
            os.makedirs(sub_folder_data)
            os.makedirs(sub_folder_domain)
            os.makedirs(sub_folder_models)
            os.makedirs(sub_folder_uploaded_files)
        except Exception as e: 
            print(e)

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        return s.getsockname()[1]

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        userID = request.form.get('userID')
        userPassword = request.form.get('userPassword')
        companyName = request.form.get('companyName')
        # global userPortNo
        userPortNo = find_free_port()
        newUser = Users(userPassword = userPassword, userId = userID, companyName = companyName, dataFolder = userID, portNo = userPortNo )
        db.session.add(newUser)
        db.session.commit()
        print(userID, userPassword)
        createFolder(userID)
        return redirect(url_for('login'))


def clearDataAndDomain(abspath):
    cmd1 = f"rm {abspath}/data/*"
    print("remove data ",cmd1)
    os.system(cmd1)
    cmd2 = f"rm {abspath}/domain/*"
    os.system(cmd2)
    cmd2 = f"rm {abspath}/uploaded_files/*"
    os.system(cmd2)


def unzip_and_move(zip_file_path, destination_path):
    # Unzip the file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path)
    
    # Get list of extracted files
    extracted_files = zip_ref.namelist()
    print(extracted_files)
    # Move files to destination based on their names
    for file_name in extracted_files:
        source_file_path = os.path.join(destination_path, file_name)
        if os.path.isfile(source_file_path):
            # Assuming file name contains the desired destination directory
            if file_name == 'domain.yml':
                destination_directory = os.path.join(destination_path,'domain')
            else:
            # destination_directory = os.path.splitext(file_name)[0]  # Remove extension
                destination_directory = os.path.join(destination_path, 'data')
            # if not os.path.exists(destination_directory):
            #     os.makedirs(destination_directory)
            shutil.move(source_file_path, destination_directory)

def killProcess():
    pid_cmd = f"lsof -ti tcp:{current_user.portNo}"
    print(pid_cmd)
    pid = subprocess.check_output(pid_cmd, shell=True).decode().strip()
    if pid :
        subprocess.run(['kill', pid])
        return True
    return False
    pass


@app.route('/stopBOT', methods=['GET'])
@login_required
def stopBOT():
    if killProcess():
        print("process killed successfully")
    else :
        print("process not found")
    return redirect(url_for('dashboard'))
    


@app.route('/retrain',methods=['GET'])
@login_required
def retrain():
    diff = current_user.countOfModels + 1
    current_user.countOfModels = diff
    db.session.commit()
    try:
        killProcess()
    except Exception as e:
        training_cmd = f"rasa train --data ./static/{current_user.userId}/data/ --domain ./static/{current_user.userId}/domain/ --out ./static/{current_user.userId}/models --fixed-model-name {current_user.userId}{diff}.tar.gz"
        print(training_cmd)
        os.system(training_cmd)
        run_cmd = (
            # f"source ./static/rasa-env/bin/activate \n"
            f"rasa run --interface 192.168.29.169 --port {current_user.portNo} ./static/{current_user.userId}/models/{current_user.userId}{diff}.tar.gz &"
        )
        os.system(run_cmd )
        print(run_cmd)
        return redirect(url_for('dashboard'))


@app.route('/startChatBot', methods=['GET'])
@login_required
def startChatBot():
    run_cmd = (
        # f"source ./static/rasa-env/bin/activate \n"
        f"rasa run --interface 192.168.29.169 --port {current_user.portNo} ./static/{current_user.userId}/models/{current_user.userId}{current_user.countOfModels}.tar.gz &"
    )
    os.system(run_cmd )
    return redirect(url_for('dashboard'))




@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    currentUser = current_user.userId
    os.system("pwd")
    if request.method == 'POST':
        file = request.files['trainingData']
        print(file)
        if file.filename == '':
            return redirect(url_for('dashboard'))
        if file : 
            abs_path = os.path.join(os.path.abspath('./static'), currentUser)
            clearDataAndDomain(abs_path) 
            file_path = os.path.join(abs_path,file.filename)
            file.save(file_path)
            unzip_and_move(file_path,abs_path)
            shutil.move(file_path,os.path.join(abs_path,'uploaded_files'))
        newFile = FilesUploaded(fileName = file.filename, fileOwner = currentUser)
        db.session.add(newFile)
        db.session.commit()
        print("post request from dashboard")
        return redirect(url_for('dashboard'))
        pass
    else :
        previous_logs = ['hello']
        data_uploaded = FilesUploaded.query.filter_by(fileOwner=currentUser).all()
        print(data_uploaded)
        abs_path = os.path.join(os.path.abspath('./static'), currentUser)
        print("absolute path - ",abs_path)
        url_for_chatbot = f"http://192.168.29.169:{current_user.portNo}/webhooks/rest/webhook"
        return render_template('dashboard2.html', previous_logs=data_uploaded, path = abs_path, url_of_chatbot = url_for_chatbot)

@login_required
@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return render_template('login.html')