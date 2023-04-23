from flask import Flask, request, render_template,redirect,url_for,session,flash,json
import base64,os,cv2
import numpy as np
from flask_pymongo import PyMongo
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

#generate masks for all the objects
def all_wop():
    if request.method=='POST':
        if (not os.path.exists('static/all_wmask_before')):
            os.makedirs('static/all_wmask_before')
        im = request.files['mask_ip']
        img_path = "static/all_wmask_before/" + im.filename	
        im.save(img_path)
        img = cv2.imread(img_path)
        hh, ww = img.shape[:2]

        # threshold on white
        # Define lower and uppper limits
        lower = np.array([10, 10, 10])
        upper = np.array([250, 250, 250])

        # Create mask to only select black
        thresh = cv2.inRange(img, lower, upper)

        # apply morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20,20))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # invert morp image
        mask = morph
        if not os.path.exists('static/all_wmask'):
            os.makedirs('static/all_wmask')
        # save results
        cv2.imwrite('static/all_wmask/'+im.filename, mask)

        #generate objects from input image on result and save it    
        if not os.path.exists('static/all_wmask/res'):
            os.makedirs('static/all_wmask/res')
        result = cv2.bitwise_and(img, img, mask=mask)
        cv2.imwrite('static/all_wmask/res/'+im.filename,result)


        #save history to database
        username=session['username']
        images= mongo.db.images
        existing_user=images.find_one({'user':username})
       
        with open("static/all_wmask_before/"+ im.filename,"rb") as file:
            encoded_image = base64.b64encode(file.read())
        with open("static/all_wmask/"+im.filename,"rb") as file2:
            encoded_image2 = base64.b64encode(file2.read())
        with open("static/all_wmask/res/"+im.filename,"rb") as op:
            encoded_op = base64.b64encode(op.read())
        

        if existing_user is None:
            images.insert_one({
                'user':username,
                'files':[{ 'input1': Binary(encoded_image), 'input2' : Binary(encoded_image2) ,'output':Binary(encoded_op) , 'type':"All White Mask" }],
                
                })
        else:
            images.update_one( {'user':username}, {"$push": {'files':{'input1': Binary(encoded_image), 'input2' : Binary(encoded_image2) ,'output':Binary(encoded_op)  , 'type':"All White Mask"} } } )
        return render_template('all_wmask.html',flag=1,filename=im.filename)
