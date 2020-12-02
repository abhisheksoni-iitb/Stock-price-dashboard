# Importing required libraries
import streamlit as st
import cv2
import numpy as np
import os

# Load Yolo
net = cv2.dnn.readNetFromDarknet("model/yolov3.cfg",
                                     "model/yolov3.weights")

classes = []
with open("classes.txt", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

def about():
	st.write(
		'''
		**Haar Cascade** is an object detection algorithm.
		It can be used to detect objects in images or videos. 

		The algorithm has four stages:

			1. Haar Feature Selection 
			2. Creating  Integral Images
			3. Adaboost Training
			4. Cascading Classifiers



Read more :point_right: https://docs.opencv.org/2.4/modules/objdetect/doc/cascade_classification.html
https://sites.google.com/site/5kk73gpu2012/assignment/viola-jones-face-detection#TOC-Image-Pyramid
		''')
 
# def main():
st.title("Face Detection App :sunglasses: ")
st.write("**Using the Haar cascade Classifiers**")

activities = ["Home", "About"]
choice = st.sidebar.selectbox("Pick something fun", activities)

if choice == "Home":

    st.write("Go to the About section from the sidebar to learn more about it.")
    
    # You can specify more file types below if you want
    image_file = st.file_uploader("Upload image", type=['jpeg', 'png', 'jpg', 'webp'])

    if image_file is not None:

        # Loading image
        # Image.open
        # pil_image = PIL.Image.open('1.jpg').convert('RGB') 
        img = np.array(image_file) 
        # Convert RGB to BGR 
        img = img[:, :, ::-1].copy() 

        # img = cv2.imread(image_file,1)
        img = cv2.resize(img, None, fx=0.9, fy=0.9)
        height, width, channels = img.shape
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        if st.button("Process"):
            # Detecting objects
            

            # Showing informations on the screen
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
            font = cv2.FONT_HERSHEY_PLAIN
            
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = colors[class_ids[i]]
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(img, label, (x, y + 30), font, 2, color, 2)


            st.image(img, use_column_width = True)
            st.success("Found {} faces\n")

elif choice == "About":
    about()




# if __name__ == "__main__":
#     main()