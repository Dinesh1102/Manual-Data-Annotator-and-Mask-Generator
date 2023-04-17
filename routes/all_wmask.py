from flask import render_template,request,json
import os
import cv2
import numpy as np

def all_wop():
    if request.method=='POST':
        if (not os.path.exists('images')):
            os.mkdir('images')
        im = request.files['mask_ip']
        img_path = "images/" + im.filename	
        im.save(img_path)
        img = cv2.imread(img_path)
        hh, ww = img.shape[:2]

        # threshold on white
        # Define lower and uppper limits
        lower = np.array([200, 200, 200])
        upper = np.array([255, 255, 255])

        # Create mask to only select black
        thresh = cv2.inRange(img, lower, upper)

        # apply morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20,20))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # invert morp image
        mask = 255 - morph
        if not os.path.exists('static/all_wmask'):
            os.makedirs('static/all_wmask')
        # save results
        cv2.imwrite('static/all_wmask/'+im.filename, mask)
        return render_template('all_wmask.html',flag=1,filename=im.filename)