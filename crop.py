from flask import Flask, request, render_template,redirect,url_for
import base64,os
from ultralytics import YOLO


app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def main():
    return render_template('temp.html')

@app.route("/crop-image", methods=['GET','POST'])
def crop_image():
    if request.method=='POST':
        if (not os.path.exists('static/cr')):
            os.makedirs('static/cr')
        img = request.files['image']
        cropped_img = request.form['croppedImage']
        filename = "static/cr/cropped"+img.filename
        tem="cropped"+img.filename
        cropped_image_decoded = base64.b64decode(cropped_img.split(',')[1])
            # save the cropped image to a file
        with open(f'{filename}', 'wb') as f:
            f.write(cropped_image_decoded)
    return render_template('temp.html',flag=1,filename=tem)

@app.route('/done',methods=['GET','POST'])
def get_output():
    if request.method=='POST':
        img = request.form['input']
        img_path = "static/cr/" + img	
        model=YOLO('yolov8n-seg.pt')
        result=model.predict(img_path,project='static',name='cr',exist_ok=True,save=True)
        return render_template('temp.html',flag=2,filename=img)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static',filename='cr/'+filename),code=301)


if __name__=='__main__':
    app.run(debug = True)
