from flask import Flask,render_template,flash,request,redirect,url_for, session,jsonify
import os
import json
from werkzeug.utils import secure_filename
# from flask_pymongo import pymongo
from flask_pymongo import PyMongo
import pymongo
import bcrypt
from pymongo import MongoClient
import cv2
import numpy as np
import mediapipe as mp

from ultralytics import YOLO
from routes.all import all_op
from routes.crop import crop_image,crop_op
from routes.video import video_op
from routes.bg_remove import bg_remove_op
from routes.bg_change import bg_change_op
from routes.manual import manual
from routes.all_wmask import all_wop
from flask_mail import *
import random

from bson.binary import Binary
# from bson.codec_options import _get_object_size
import base64


app = Flask(__name__ ,  static_url_path='/static')

# with open("config.json" , "r" ) as f :
#     params = json.load(f)["params"]
 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'sonikabatchu@gmail.com'
app.config['MAIL_PASSWORD'] = 'nfhzugtgocngwina'

# Create an instance of Flask-Mail
mail = Mail(app)
otp = random.randint(1000 , 9999)

# UPLOAD_FOLDER

app.config["MONGO_DBNAME"] = 'maskgenerator'
app.config['MONGO_URI'] = "mongodb://localhost:27017/maskgenerator"

# mongo = PyMongo(app)

mongo_uri = "mongodb://localhost:27017/maskgenerator"
mongo = PyMongo(app, uri=mongo_uri)



ALLOWED_EXTENSIONS =set(['png','jpg','jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def b64encode(value):
    return base64.b64encode(value).decode('utf-8')

# Add the b64encode filter to the Jinja2 environment
app.jinja_env.filters['b64encode'] = b64encode

@app.route('/')
def main():
    return render_template('mainpage.html')


@app.route('/history',methods=["POST",'GET'])
def history():
    images = mongo.db.images
    user = images.find_one({'user': session['username']})
    decoded_images= []
    decoded_images_bg_change= []
    

    if user :
        for obj in user['files']:
            if 'input' in obj and 'output' in obj  :
                image_bytes = base64.b64decode(obj['input'])
                image_bytes_output = base64.b64decode(obj['output'])
                new_obj = {'input': image_bytes , 'output' :image_bytes_output  , "type" : obj['type']}
                decoded_images.append(new_obj)
            elif  'input1' in obj and 'input2'in obj and "output" in obj:
                image_bytes = base64.b64decode(obj['input1'])
                image_bytes_input2 = base64.b64decode(obj['input2'])
                image_bytes_output = base64.b64decode(obj['output'])
                new_obj = {'input1': image_bytes , 'input2' : image_bytes_input2 , 'output' :image_bytes_output , "type" : obj["type"]}
                decoded_images_bg_change.append(new_obj)

            
    else:
        
        return render_template('history.html' , i = decoded_images , j=decoded_images_bg_change , flag =0)
    



    return render_template('history.html' , i = decoded_images , j=decoded_images_bg_change , flag=1)


    


@app.route('/home')
def home():
    
    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'): 
            return render_template('home.html')
    flash("Seems like your not logged in, please login first",'danger')
    return render_template('login.html') 

        
@app.route('/login' , methods=['POST' , 'GET'])
def login():
    if request.method == "POST":
        users= mongo.db.users
        login_user=users.find_one({'name':request.form['username']})
        if login_user:
            # entered_password_hashed = bcrypt.hashpw(request.form['pass'].encode('utf-8') , bcrypt.gensalt())
            entered_password_hashed = request.form['pass'].encode('utf-8')
            if bcrypt.checkpw(entered_password_hashed, login_user['password']) and login_user['verify'] == 'true':
                session["username"]=request.form['username']
                session['password'] = request.form['pass']
                session['verify']= login_user['verify']
                flash('HELLO '+ session['username'].upper()+". You are successfully logged in!",'success')
                return redirect(url_for('home'))
            
        flash('Invalid Credentials','danger')
        return render_template('login.html')
    
    return render_template("login.html")

@app.route('/verify' , methods=['POST' , "GET"]) 
def verify():
    if(request.method == "POST"):
        if(str(otp) == request.form['entered_otp']):
            users= mongo.db.users
            users.update_one( {"name" : session['username']}  , {"$set" :{"verify" : "true"}})
            session['verify'] = "true"
            flash("You are successfully registered!!",'success')
            return redirect(url_for('home'))
        else:
            users= mongo.db.users
            users.delete_one({"name" : session['username']})
            flash('Invalid otp , try registering again!!!','danger')
            return redirect(url_for('register'))
        
    return render_template('verify.html') 
        

@app.route('/register' , methods =['POST' , "GET"])
def register():
    if request.method == "POST":

        if request.form['pass'] != request.form['cpass']:
            return render_template("register.html")
        users= mongo.db.users
        existing_user = users.find_one({ 'name' : request.form['username']})
        

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8') , bcrypt.gensalt())
            users.insert_one({ 'name' : request.form['username'] , "password" : hashpass , 'first_name' : request.form['fname'] , 'last_name' : request.form['lname']  , 'email' : request.form['email'] , 'verify' : 'false'})
            session['username'] = request.form['username']
            session['verify'] = 'false'
            email = request.form['email']
            msg = Message('VERIFY YOUR ACCOUNT' , sender = 'sonikabatchu@gmail.com' , recipients=[email])
            msg.body = "Your confirmation otp is : " + str(otp)
            mail.send(msg)
            flash("We have sent you a confirmation email, please enter the otp to activate your account",'message')
            return redirect(url_for('verify'))
        else :
           if existing_user['verify'] == 'true':
                flash('The username already exists','danger')
                return render_template('register.html')
           else:
               users.delete_one({"name" : existing_user['name']})
               hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8') , bcrypt.gensalt())
               users.insert_one({ 'name' : request.form['username'] , "password" : hashpass , 'first_name' : request.form['fname'] , 'last_name' : request.form['lname']  , 'email' : request.form['email'] , 'verify' : 'false'})
               session['username'] = request.form['username']
               session['verify'] = 'false'
               email = request.form['email']
               msg = Message('VERIFY YOUR ACCOUNT' , sender = 'sonikabatchu@gmail.com' , recipients=[email])
               msg.body = "Your confirmation otp is : " + str(otp)
               mail.send(msg)
               flash("We have sent you a confirmation email, please enter the otp to activate your account",'message')
               return redirect(url_for('verify'))
               
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    # session['username']= null
    session.pop('username', None)
    flash('You have successfully logged out!','success')
    return render_template('mainpage.html')

@app.route('/all')
def all():

    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'):
            return render_template('all.html')
        
    return render_template('login.html') 
    
    

@app.route('/crop' )
def crop():

    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'):
            return render_template('crop.html')
        
    return render_template('login.html') 
  

@app.route('/video' )
def video():

    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'):
            return render_template('video.html')
        
    return render_template('login.html') 
    

@app.route('/bg_remove' )
def bg_remove():
    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'):
            return render_template('bg_remove.html')
        
    return render_template('login.html')
    


@app.route('/bg_change')
def bg_change():
    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'):
            return render_template('bg_change.html')
        
    return render_template('login.html')


#All masks
@app.route('/submit_all',methods=['POST'])
def submit_all():

    UPLOAD_FOLDER="static/all_before"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']=16*1024*1024
    file=request.files['my_image']
    filename=secure_filename(file.filename)
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return all_op(file.filename)

    else:
        flash('Invalid, upload only txt, pdf, png, jpg, jpeg, gif','danger')
        return render_template('all.html')
    

   

@app.route('/display_all/<filename>')
def display_image_all(filename):
    return redirect(url_for('static',filename='predict/'+filename),code=301)



#Selected objects
@app.route('/cropimage',methods=['POST'])
def cropimage():
    

    UPLOAD_FOLDER="static/crop_before"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']=16*1024*1024
    file=request.files['image']
    filename=secure_filename(file.filename)
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return crop_image()

    else:
        flash('Invalid, upload only txt, pdf, png, jpg, jpeg, gif','danger')
        return render_template('crop.html')
   

@app.route('/crop_res',methods=['POST'])
def cropres():
    return crop_op()

@app.route('/display_crop/<filename>')
def display_image_crop(filename):
    return redirect(url_for('static',filename='cropped/'+filename),code=301)

@app.route('/display_crop_res/<filename>')
def display_image_crop_res(filename):
    return redirect(url_for('static',filename='cr/'+filename),code=301)

#Video

@app.route('/submit_video',methods=['POST'])
def submit_video():
    return video_op()

@app.route('/display_video_res/<filename>')
def display_video(filename):
    return redirect(url_for('static',filename='vid_pred/'+filename),code=301)

# bg_remove
@app.route('/submit_bg_remove',methods=['POST'])
def submit_bg_remove():

    UPLOAD_FOLDER="static/bg_remove_before"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']=16*1024*1024
    file=request.files['my_image']
    filename=secure_filename(file.filename)
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return bg_remove_op(file.filename)

    else:
        flash('Invalid, upload only txt, pdf, png, jpg, jpeg, gif','danger')
        return render_template('bg_remove.html')



@app.route('/display_bg_remove/<filename>')
def display_bg_remove(filename):
    return redirect(url_for('static',filename='bg_removed/'+filename),code=301)

#bg_change
@app.route('/submit_bg_change',methods=['POST'])

def submit_bg_change():

    UPLOAD_FOLDER="static/bg_change_before"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']=16*1024*1024
    file=request.files['my_image']
    filename=secure_filename(file.filename)
    file2=request.files['bg']
    filename2 = secure_filename(file2.filename)
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'],filename2))
        return bg_change_op(file.filename , file2.filename)

    else:
        flash('Invalid, upload only txt, pdf, png, jpg, jpeg, gif','danger')
        return render_template('bg_change.html')
    
@app.route('/display_bg_change/<filename>')
def display_bg_change(filename):
    return redirect(url_for('static',filename='bg_changed/'+filename),code=301)


# new
@app.route('/all_wmask' )
def all_wmask():
    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'):
            return render_template('all_wmask.html')
    return render_template('login.html')


@app.route('/Mmask')
def Mmask():
    if 'username' in session :
        verified = session['verify']
        if(verified == 'true'):
            return render_template('Mmask.html')
    return render_template('login.html')

@app.route('/mask_upload',methods=['POST'])
def mask_upload():
    return manual()

@app.route('/display_manual/<filename>')
def display_manual(filename):
    return redirect(url_for('static',filename='manual/'+filename),code=301)

@app.route('/display_manual_res/<filename>')
def display_manual_res(filename):
    return redirect(url_for('static',filename='manual/res/'+filename),code=301)


#All White masks
@app.route('/submit_all_wmask',methods=['POST'])
def submit_all_wmask():
    return all_wop()

@app.route('/display_image_all_wmask/<filename>')
def display_image_all_wmask(filename):
    return redirect(url_for('static',filename='all_wmask/'+filename),code=301)

@app.route('/display_image_all_wmask_res/<filename>')
def display_image_all_wmask_res(filename):
    return redirect(url_for('static',filename='all_wmask/res/'+filename),code=301)

if __name__=='__main__':
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.run(debug = True)
