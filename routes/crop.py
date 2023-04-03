from flask import Flask, request, render_template,redirect,url_for
import base64,os
from ultralytics import YOLO

def crop_image():
    if request.method=='POST':
        if (not os.path.exists('static/cropped')):
            os.makedirs('static/cropped')
        img = request.files['image']
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
        return render_template('crop.html',flag=2,filename=img)