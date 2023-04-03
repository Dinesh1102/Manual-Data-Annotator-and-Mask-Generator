from flask import Flask,render_template,request,redirect,url_for
import os
from ultralytics import YOLO
from routes.all import all_op
from routes.crop import crop_image,crop_op
from routes.video import video_op
from routes.bg_remove import bg_remove_op
from routes.bg_change import bg_change_op
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/all')
def all():
    return render_template('all.html')

@app.route('/crop' )
def crop():
    return render_template('crop.html')

@app.route('/video' )
def video():
    return render_template('video.html')

@app.route('/bg_remove' )
def bg_remove():
    return render_template('bg_remove.html')

@app.route('/bg_change')
def bg_change():
    return render_template('bg_change.html')


#All masks
@app.route('/submit_all',methods=['POST'])
def submit_all():
    return all_op()

@app.route('/display_all/<filename>')
def display_image_all(filename):
    return redirect(url_for('static',filename='predict/'+filename),code=301)


#Selected objects
@app.route('/cropimage',methods=['POST'])
def cropimage():
    return crop_image()

@app.route('/crop_res',methods=['POST'])
def cropres():
    return crop_op()

@app.route('/display_crop/<filename>')
def display_image_crop(filename):
    return redirect(url_for('static',filename='cropped/'+filename),code=301)

@app.route('/display_crop_res/<filename>')
def display_image_crop_res(filename):
    return redirect(url_for('static',filename='cr/'+filename),code=301)

#Video

@app.route('/submit_video',methods=['POST'])
def submit_video():
    return video_op()

@app.route('/display_video_res/<filename>')
def display_video(filename):
    return redirect(url_for('static',filename='vid_pred/'+filename),code=301)

# bg_remove
@app.route('/submit_bg_remove',methods=['POST'])
def submit_bg_remove():
    return bg_remove_op()

@app.route('/display_bg_remove/<filename>')
def display_bg_remove(filename):
    return redirect(url_for('static',filename='bg_removed/'+filename),code=301)

#bg_change
@app.route('/submit_bg_change',methods=['POST'])
def submit_bg_change():
    return bg_change_op()

@app.route('/display_bg_change/<filename>')
def display_bg_change(filename):
    return redirect(url_for('static',filename='bg_changed/'+filename),code=301)



if __name__=='__main__':
    app.run(debug = True)


