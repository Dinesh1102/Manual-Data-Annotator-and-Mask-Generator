from flask import Flask, request, render_template,redirect,url_for,session,flash
import base64,os,cv2
from ultralytics import YOLO
from flask_pymongo import PyMongo
import pymongo
import bcrypt
import json
from pymongo import MongoClient
from werkzeug.utils import secure_filename

from bson.binary import Binary
# from bson.codec_options import _get_object_size
import base64
app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'maskgenerator'
app.config['MONGO_URI'] = "mongodb://localhost:27017/maskgenerator"

# mongo = PyMongo(app)

mongo_uri = "mongodb://localhost:27017/maskgenerator"
mongo = PyMongo(app, uri=mongo_uri)


def b64encode(value):
    return base64.b64encode(value).decode('utf-8')

# Add the b64encode filter to the Jinja2 environment
app.jinja_env.filters['b64encode'] = b64encode


# UPLOAD_FOLDER="static/cr"
# app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH']=16*1024*1024

# ALLOWED_EXTENSIONS =set(['txt','pdf','png','jpg','jpeg','gif'])

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def crop_image():
    if request.method=='POST':
        if (not os.path.exists('static/cropped')):
            os.makedirs('static/cropped')
        img = request.files['image']
        # session['image']=img
        cropped_img = request.form['croppedImage']
        filename = "static/cropped/"+img.filename
        cropped_image_decoded = base64.b64decode(cropped_img.split(',')[1])
            # save the cropped image to a file
        with open(f'{filename}', 'wb') as f:
            f.write(cropped_image_decoded)
    return render_template('crop.html',flag=1,filename=img.filename)

def crop_op():
    if request.method=='POST':
        img = request.form['input']
        img_path = "static/cropped/" + img	
        model=YOLO('yolov8n-seg.pt')
        result=model.predict(img_path,project='static',name='cr',exist_ok=True,save=True)

        username=session['username']
        images= mongo.db.images
        existing_user=images.find_one({'user':username})
        # file=cv2.imread("static/crop_before/"+img)
        with open("static/crop_before/"+img,"rb") as file:
            encoded_image = base64.b64encode(file.read())
        with open("static/cr/"+img,"rb") as op:
            encoded_op = base64.b64encode(op.read())
        # op=cv2.imread("static/cr/"+img)
        # encoded_op = base64.b64encode(op)

        if existing_user is None:
            images.insert_one({
                'user':username,
                'files':[{ 'input':Binary(encoded_image),'output':Binary(encoded_op) ,  "type" : "Selection"}]
                })
        else:
            images.update_one( {'user':username}, {"$push": {'files':{'input': Binary(encoded_image),'output':Binary(encoded_op) ,  "type" : "Selection"} } } )
        
        
        



    return render_template('crop.html',flag=2,filename=img)