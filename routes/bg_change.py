from flask import Flask,render_template,request,redirect,url_for,session
import cv2,os
import numpy as np
import mediapipe as mp
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


def bg_change_op(file1name , file2name):
    if request.method=='POST':
        # if (not os.path.exists('images')):
        #     os.mkdir('images')
        # img = request.files['my_image']
        img_path = "static/bg_change_before/" + file1name	
        # img.save(img_path)
        # bg = request.files['bg']
        bg_path = "static/bg_change_before/" + file2name	
        # bg.save(bg_path)
        change_background_mp = mp.solutions.selfie_segmentation
        change_bg_segment = change_background_mp.SelfieSegmentation()
        sample_img = cv2.imread(img_path)
        RGB_sample_img = cv2.cvtColor(sample_img, cv2.COLOR_BGR2RGB)
        result = change_bg_segment.process(RGB_sample_img)
        binary_mask = result.segmentation_mask > 0.9
        binary_mask_3 = np.dstack((binary_mask,binary_mask,binary_mask))
        h,w,c = sample_img.shape
        bg = cv2.imread(bg_path)
        bg = cv2.resize(bg,(w,h))
        changed = np.where(binary_mask_3, sample_img, bg) 
        if(not os.path.exists('static/bg_changed')):
            os.makedirs('static/bg_changed')  
        result_path =  "static/bg_changed/"+file1name
        print(result_path)
        cv2.imwrite(result_path,changed)



        username=session['username']
        images= mongo.db.images
        existing_user=images.find_one({'user':username})
        # file=cv2.imread("static/crop_before/"+img)
        with open("static/bg_change_before/"+ file1name,"rb") as file:
            encoded_image = base64.b64encode(file.read())
        with open("static/bg_change_before/"+file2name,"rb") as file2:
            encoded_image2 = base64.b64encode(file2.read())
        with open("static/bg_changed/"+file1name,"rb") as op:
            encoded_op = base64.b64encode(op.read())
        # op=cv2.imread("static/cr/"+img)
        # encoded_op = base64.b64encode(op)

        if existing_user is None:
            images.insert_one({
                'user':username,
                'files':[{ 'input1': Binary(encoded_image), 'input2' : Binary(encoded_image2) ,'output':Binary(encoded_op) , 'type':"Background Change" }],
                
                })
        else:
            images.update_one( {'user':username}, {"$push": {'files':{'input1': Binary(encoded_image), 'input2' : Binary(encoded_image2) ,'output':Binary(encoded_op)  , 'type':"Background Change"} } } )
        
        return render_template('bg_change.html',flag=1,filename=file1name)