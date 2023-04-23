from flask import Flask,render_template,request,json,flash,session
import os,cv2,shutil
import numpy as np
from flask_pymongo import PyMongo
import json
from bson.binary import Binary
import base64

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'maskgenerator'
app.config['MONGO_URI'] = "mongodb://localhost:27017/maskgenerator"


mongo_uri = "mongodb://localhost:27017/maskgenerator"
mongo = PyMongo(app, uri=mongo_uri)


def b64encode(value):
    return base64.b64encode(value).decode('utf-8')

# Add the b64encode filter to the Jinja2 environment
app.jinja_env.filters['b64encode'] = b64encode

# generate masks for objects inside the loops 
def manual():
    if request.method=="POST":
        im=request.files['imageLoader']
        if (not os.path.exists('static/manual_before')):
            os.makedirs('static/manual_before')
        im_path='static/manual_before/'+im.filename
        im.save(im_path)
        img = cv2.imread(im_path)
        #coordinates of loops from html stored in data
        data = request.form.get('coordinates')
        data=json.loads(data)
        #show results  if atleast one loop is closed
        if data:
            result=[]
            #append coordinates in result which is a 3d list
            for i in data:
                if not i==None:
                    temp=[]
                    for j in i:
                        temp.append([j['x'],j['y']])
                    result.append(temp)
            cnt=0
            #filling individual loops in white inside an black image of same dimensions as input image and storing them in static/results
            for i in result:
                cnt+=1
                H , W , _ = img.shape
                mask = np.zeros((H, W), dtype=np.uint8)
                points = np.array([i])
                
                cv2.fillPoly(mask, points, (255))
                if not os.path.exists('static/results'):
                    os.makedirs('static/results')
                cv2.imwrite(f"static/results/{cnt}"+im.filename , mask )
            # deleting previous results of same image   
            if os.path.exists('static/manual'):
                shutil.rmtree('static/manual')
            # applying bitwise_or on all images in static/results
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
            # showing original objects of only those inside loops with black background
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
            

            return render_template('Mmask.html',filename=im.filename,flag=1)
        #if data is empty return to the page as loop is not closed
        else:
            flash('Loop not closed !!','danger')
            return render_template('Mmask.html')
