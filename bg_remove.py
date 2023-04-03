from flask import Flask,render_template,request,redirect,url_for
import cv2
import numpy as np
import mediapipe as mp
app = Flask(__name__)
@app.route('/',methods=['GET','POST'])
def main():
    return render_template('bg_remove.html')

@app.route('/submit',methods=['GET','POST'])
def get_output():
    if request.method=='POST':
        img = request.files['my_image']
        img_path = "images/" + img.filename	
        img.save(img_path)
        change_background_mp = mp.solutions.selfie_segmentation
        change_bg_segment = change_background_mp.SelfieSegmentation()
        sample_img = cv2.imread(img_path)
        RGB_sample_img = cv2.cvtColor(sample_img, cv2.COLOR_BGR2RGB)
        result = change_bg_segment.process(RGB_sample_img)
        binary_mask = result.segmentation_mask > 0.9
        binary_mask_3 = np.dstack((binary_mask,binary_mask,binary_mask))
        output_image = np.where(binary_mask_3, sample_img, 255)   
        result_path =  "static/bg_removed/"+img.filename
        print(result_path)
        cv2.imwrite(result_path,output_image)
        return render_template('bg_remove.html',flag=1,filename=img.filename)


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static',filename='bg_removed/'+filename),code=301)


if __name__=='__main__':
    app.run(debug = True)