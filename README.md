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
  
![](assets/pills.jpeg)

 2. Instance Segmentation For All Objects
  Model generates a mask along with label and accuracy score for all the detected objects in the image.
  
![](assets/instanceforall.jpg)
