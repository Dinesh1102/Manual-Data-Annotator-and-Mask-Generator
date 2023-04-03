from flask import Flask,render_template,request,redirect,url_for
import cv2,os
import numpy as np
import mediapipe as mp

def bg_change_op():
    if request.method=='POST':
        if (not os.path.exists('images')):
            os.mkdir('images')
        img = request.files['my_image']
        img_path = "images/" + img.filename	
        img.save(img_path)
        bg = request.files['bg']
        bg_path = "images/" + bg.filename	
        bg.save(bg_path)
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
        result_path =  "static/bg_changed/"+img.filename
        print(result_path)
        cv2.imwrite(result_path,changed)
        return render_template('bg_change.html',flag=1,filename=img.filename)


