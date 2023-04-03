from flask import Flask,render_template,request,redirect,url_for
import os
from ultralytics import YOLO

def all_op():
    if request.method=='POST':
        if (not os.path.exists('images')):
            os.mkdir('images')
        img = request.files['my_image']
        img_path = "images/" + img.filename	
        img.save(img_path)
        model=YOLO('yolov8n-seg.pt')
        result=model.predict(img_path,project='static',exist_ok=True,save=True)
        return render_template('all.html',flag=1,filename=img.filename)
