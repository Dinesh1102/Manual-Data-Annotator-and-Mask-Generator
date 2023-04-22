from flask import Flask, render_template,request,json , session
import os,cv2,shutil, base64
import numpy as np
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

def manual():
    if request.method=="POST":
        im=request.files['imageLoader']
        if not os.path.exists('images'):
            os.makedirs('images')
        im_path='images/'+im.filename
        im.save(im_path)
        img = cv2.imread(im_path)
        data = request.form.get('coordinates')
        data=json.loads(data)
        result=[]
        for i in data:
            if not i==None:
                temp=[]
                for j in i:
                    temp.append([j['x'],j['y']])
                result.append(temp)
        cnt=0
        for i in result:
            cnt+=1
            H , W , _ = img.shape
            mask = np.zeros((H, W), dtype=np.uint8)
            points = np.array([i])
            cv2.fillPoly(mask, points, (255))
            if not os.path.exists('static/results'):
                os.makedirs('static/results')
            cv2.imwrite(f"static/results/{cnt}"+im.filename , mask )
        if os.path.exists('static/manual'):
            shutil.rmtree('static/manual')
        for i in range(1,cnt+1):
            cur=cv2.imread(f"static/results/{i}"+im.filename)
            if i==1:
                if not os.path.exists('static/manual'):
                    os.makedirs('static/manual')
                cv2.imwrite("static/manual/"+im.filename , cur)
            else:
                bg=cv2.imread("static/manual/"+im.filename )
                res=cv2.bitwise_or(cur,bg,mask=None)
                cv2.imwrite("static/manual/"+im.filename , res)
        if not os.path.exists('static/manual/res'):
            os.makedirs('static/manual/res')
        tem =cv2.imread("static/manual/"+im.filename)
        resu=cv2.bitwise_and(img,tem,mask=None)
        cv2.imwrite("static/manual/res/"+im.filename,resu)
        if os.path.exists('static/results'):
            shutil.rmtree('static/results')



        username=session['username']
        images= mongo.db.images
        existing_user=images.find_one({'user':username})
        # file=cv2.imread("static/crop_before/"+img)
        with open("images/"+ im.filename,"rb") as file:
            encoded_image = base64.b64encode(file.read())
        with open("static/manual/"+im.filename,"rb") as file2:
            encoded_image2 = base64.b64encode(file2.read())
        with open("static/manual/res/"+im.filename,"rb") as op:
            encoded_op = base64.b64encode(op.read())
        # op=cv2.imread("static/cr/"+img)
        # encoded_op = base64.b64encode(op)

        if existing_user is None:
            images.insert_one({
                'user':username,
                'files':[{ 'input1': Binary(encoded_image), 'input2' : Binary(encoded_image2) ,'output':Binary(encoded_op) , 'type':"Manual Mask Generator" }],
                
                })
        else:
            images.update_one( {'user':username}, {"$push": {'files':{'input1': Binary(encoded_image), 'input2' : Binary(encoded_image2) ,'output':Binary(encoded_op)  , 'type':"Manual Mask Generator"} } } )
        
        # return render_template('bg_change.html',flag=1,filename=file1name)


        return render_template('Mmask.html',filename=im.filename,flag=1)