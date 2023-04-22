# Manual Data Annotator and Mask Generator

# Description
 An application that will generate a segmentation mask for a given image. The end user drags the mouse pointer and forms a closed loop on the given image. All the pixels in the given loop (along with the boundary) will act as the mask for the given image.
 
 ![](assets/braintumor.jpeg)
 
 End user drags the mouse pointer around the desired object to form a loop so that a white mask is generated around it.
 
 ![](assets/nuclei.jpeg)
 
 End user can use polylines (by marking points) to form a loop and generate a mask.
 
 # Extended Features
 
 1. Generating White Masks For All Objects
  A white mask is generated around all the objects detected by the model.
  
![](assets/pills.jpeg=250x250)

 2. Instance Segmentation For All Objects
  Model generates a mask along with label and accuracy score for all the detected objects in the image.
  
![](assets/instanceforall.jpg)

3. Selective Segmentation
End user draws a bounding box and all the objects inside the box are segmented and labelled.

![](assets/selective)

4. Background Removal
Background is removed for all the objects whose accuracy score is > 90%

![](assets/bgremove)

5. Background Change
Background is changed for all the objects whose accuracy score is >90%

![](assets/bgchange.jpeg)

6. Object Detection For Video
