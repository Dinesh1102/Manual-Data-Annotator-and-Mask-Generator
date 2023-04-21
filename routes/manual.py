from flask import render_template,request,json
import os,cv2,shutil
import numpy as np

def manual():
    if request.method=="POST":
        im=request.files['imageLoader']
        if not os.path.exists('images'):
            os.makedirs('images')
        im_path='images/'+im.filename
        im.save(im_path)
        img = cv2.imread(im_path)
        data = request.form.get('coordinates')
        data=json.loads(data)
        result=[]
        for i in data:
            if not i==None:
                temp=[]
                for j in i:
                    temp.append([j['x'],j['y']])
                result.append(temp)
        cnt=0
        for i in result:
            cnt+=1
            H , W , _ = img.shape
            mask = np.zeros((H, W), dtype=np.uint8)
            points = np.array([i])
            cv2.fillPoly(mask, points, (255))
            if not os.path.exists('static/results'):
                os.makedirs('static/results')
            cv2.imwrite(f"static/results/{cnt}"+im.filename , mask )
        if os.path.exists('static/manual'):
            shutil.rmtree('static/manual')
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
        resu=cv2.bitwise_and(img,tem,mask=None)
        cv2.imwrite("static/manual/res/"+im.filename,resu)
        if os.path.exists('static/results'):
            shutil.rmtree('static/results')
        return render_template('Mmask.html',filename=im.filename,flag=1)
