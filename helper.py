# Importing required libraries
import streamlit as st
import cv2
import numpy as np
import os
import PIL
from PIL import Image
import base64
from io import BytesIO
from matplotlib import pyplot as plt
%matplotlib inline
# Load Yolo
net = cv2.dnn.readNetFromDarknet("model/yolov3.cfg",
                                     "model/yolov3.weights")

classes = []
with open("model/classes.txt", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

def about():
	st.write('')

def get_optimal_font_scale(text, width):
    for scale in reversed(range(0, 10, 1)):
        textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
        new_width = textSize[0][0]
    # print(new_width)
        if (new_width <= width):
            return scale/10
    return 1 


cap = cv2.VideoCapture('123.mp4')
frame_width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))

frame_height =int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
plt.show()
# out = cv2.VideoWriter("output.avi", fourcc, 5.0, (1280,720))
# out = cv2.VideoWriter('output.avi', -1, 20.0, (1280,720))
from skvideo.io import VideoWriter_fourcc
# import numpy
writer = VideoWriter_fourcc('output.avi', frameSize=(1280,720))



success = True
while success:
    success, img= cap.read()
    if success:
        # image = Image.open(image_file)
        # img = np.array(image.convert('RGB'))

        # img = cv2.resize(img, None, fx=0.9, fy=0.9)
        height, width, channels = img.shape
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        # if st.button("Process"):

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        # print(indexes)
        font = cv2.FONT_HERSHEY_DUPLEX

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                label+=', '
                label+= str((round(confidences[i],2)*100))
                label+= '%'
                color = colors[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
                # cv2.putText(img, label, (x, y + 15), font,  0.5, color, 2)

                # Draw black background rectangle
                cv2.rectangle(img, (x, y), (x + int(w),y + int(h/15)), (255,255,255), -1)

                # Add text
                fontscale = get_optimal_font_scale(label, width)
                cv2.putText(img, label, (x + int(w/20),y + int(h/20)), font,  fontscale, (0,0,0),lineType=cv2.LINE_AA)
        img = cv2.resize(img, (1280,720))
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
        output.write(img)
        plt.imshow(img)
        plt.show()
           
cap.release()
    
       