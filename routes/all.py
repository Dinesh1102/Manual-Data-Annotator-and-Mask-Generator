from flask import Flask,render_template,request,redirect,url_for,session
import os
from ultralytics import YOLO
from flask_pymongo import PyMongo
import pymongo
import bcrypt
import json
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson.binary import Binary
import base64

app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'maskgenerator'
app.config['MONGO_URI'] = "mongodb://localhost:27017/maskgenerator"


mongo_uri = "mongodb://localhost:27017/maskgenerator"
mongo = PyMongo(app, uri=mongo_uri)

#encode images as base64 strings 
def b64encode(value):
    return base64.b64encode(value).decode('utf-8')

# Add the b64encode filter to the Jinja2 environment
app.jinja_env.filters['b64encode'] = b64encode


#run predictions on image using yolov8n model
def all_op(filename):
    if request.method=='POST':
        if (not os.path.exists('images')):
            os.mkdir('images')

        img_path = "static/all_before/" + filename	
        
        model=YOLO('yolov8n-seg.pt')
        result=model.predict(img_path,project='static',exist_ok=True,save=True)


        #save to database
        username=session['username']
        images= mongo.db.images
        existing_user=images.find_one({'user':username})
        with open("static/all_before/"+filename,"rb") as file:
            encoded_image = base64.b64encode(file.read())
        with open("static/predict/"+filename,"rb") as op:
            encoded_op = base64.b64encode(op.read())
        
        if existing_user is None:
            images.insert_one({
                'user':username,
                'files':[{ 'input':Binary(encoded_image),'output':Binary(encoded_op) , 'type': "All Masks"}]
                })
        else:
            images.update_one( {'user':username}, {"$push": {'files':{'input': Binary(encoded_image),'output':Binary(encoded_op) , 'type': "All Masks"} } } )


        return render_template('all.html',flag=1,filename=filename)
