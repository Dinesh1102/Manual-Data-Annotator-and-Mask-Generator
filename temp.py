from ultralytics import YOLO
import cv2
import os

# Open the video file
vidcap = cv2.VideoCapture('images/soccer_fight360p.mp4')
fps = vidcap.get(cv2.CAP_PROP_FPS)
width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
if not os.path.exists('frames'):
    os.makedirs('frames')
success=True
model = YOLO('yolov8n-seg.pt')
count=0
while success:
    # Process the frame here
    # processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    success, image = vidcap.read()
    current_frame = vidcap.get(cv2.CAP_PROP_POS_FRAMES)
    # Save the processed frame as an image
    if success:
        cv2.imwrite(f'frames/img_frame_{count}.jpg', image)
        count+=1

ip = "frames"
count=0
for f in os.listdir('frames'):
    if f.endswith('.jpg'):
        count+=1
        print(count)
        results = model('frames/'+f,project='op',save=True,exist_ok=True)

from moviepy.editor import ImageSequenceClip,VideoFileClip

# Set the path for the input images and output video
input_path = "op/predict"
output_path = "pls.mp4"

# Set the duration of each image in the video (in seconds)
temp = VideoFileClip('images/soccer_fight360p.mp4')
# Get the list of image file names in the input path
image_files = sorted([f for f in os.listdir(input_path) if f.endswith('.jpg')])

# Create an image sequence clip from the input images
clip = ImageSequenceClip([os.path.join(input_path, f) for f in image_files], fps=temp.fps)

# Write the clip to a video file
clip.write_videofile(output_path)
import shutil
if os.path.exists('op'):
    shutil.rmtree('op')
if os.path.exists('frames'):
    shutil.rmtree('frames')
print("Video generated successfully!")