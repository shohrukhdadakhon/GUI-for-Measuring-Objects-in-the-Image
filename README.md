# GUI-for-Measuring-Objects-in-the-Image

OBJECT SIZE MEASUREMENT FROM AN IMAGE USING A REFERENCE IMAGE ON A PLAIN BACKGROUND

HOW TO USE THE GUI:

1. Run the GUI: Run the main.py inside the "codes" file.

2. Select Image: You can select an image for object size measurement from the "Images for measurement" file location by clicking the "Select Image" button on the GUI.

3. Enter width of the reference object: You should enter the width of the reference object which you have located to left-most of the image. In our images: 50 Kuruş = 23.85 mm, 1 TL = 26.15 mm.

4. Select unit of width: Select the unit of width (mm, cm, m, in, ft) of the reference object using the drop-down menu on the right of the width input.

5. Select the contour area: Contour area is used to decide on the which sized objects will be detected. If you have small objects on the image you can decrease the "min" value 
so the algorithm can detect objects which have small contour area. Similarly you can increase the "max" value if you want to detect larger objects on the image. Recommended 
values are default values which are already written when you run the GUI. Default values are determined based on our images which are located in "Images for measurement" file.

6. Detect: Click the detect button. A window will pop up which has the reference object size written and marked with rectangle around the object. You should click the "NEXT" arrow 
from your keyboard to see the next detected object. Do this until it stops detecting so you can see all objects on image with their sizes marked.


* For perfect accurate measurement images should be top-down view on objects.
* Background of images should be plain so the algorithm won't have problems while detecting contours.
