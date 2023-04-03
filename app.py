from flask import Flask,render_template,request,redirect,url_for
import os
from ultralytics import YOLO
app = Flask(__name__)
@app.route('/',methods=['GET','POST'])
def main():
    return render_template('index.html')

@app.route('/submit',methods=['GET','POST'])
def get_output():
    if request.method=='POST':
        img = request.files['my_image']
        img_path = "images/" + img.filename	
        img.save(img_path)
        model=YOLO('yolov8s-seg.pt')
        result=model.predict(img_path,project='static',exist_ok=True,save=True)
        return render_template('index.html',flag=1,filename=img.filename)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static',filename='predict/'+filename),code=301)

if __name__=='__main__':
    app.run(debug = True)