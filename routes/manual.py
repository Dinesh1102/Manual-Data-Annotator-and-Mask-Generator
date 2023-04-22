from flask import render_template,request,json,flash
import os,cv2,shutil
import numpy as np
# generate masks for objects inside the loops 
def manual():
    if request.method=="POST":
        im=request.files['imageLoader']
        if not os.path.exists('images'):
            os.makedirs('images')
        im_path='images/'+im.filename
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
            return render_template('Mmask.html',filename=im.filename,flag=1)
        #if data is empty return to the page as loop is not closed
        else:
            flash('Loop not closed !!','danger')
            return render_template('Mmask.html')
