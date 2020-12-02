# Importing required libraries
import streamlit as st
import cv2
import numpy as np
import os
import PIL
from PIL import Image
import base64
from io import BytesIO

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

def main():
    st.title("Object detection App")
    st.write("")

    activities = ["Home", "About"]
    choice = st.sidebar.selectbox("Section", activities)

    if choice == "Home":

        confidence_threshold = st.sidebar.slider("Confidence threshold", 0.0, 1.0, 0.5, 0.01)                
        # You can specify more file types below if you want
        image_file = st.file_uploader("Upload image", type=['jpeg', 'png', 'jpg', 'webp'])

        if image_file is not None:


            image = Image.open(image_file)
            img = np.array(image.convert('RGB'))

            img = cv2.resize(img, None, fx=0.9, fy=0.9)
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
                    if confidence > confidence_threshold:
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
                    # cv2.putText(image, "THICC flower", (x + int(w/10),y + int(h/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
           
            st.image(img, use_column_width = True)

            def download_link(img):
                """Generates a link allowing the PIL image to be downloaded
                in:  PIL image
                out: href string
                """
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                href = f'<a href="data:file/jpg;base64,{img_str}" download="processed.png">Download File</a>'
                return href

            if st.button('Create Download Link'):
                result = Image.fromarray(img)
                st.markdown(download_link(result), unsafe_allow_html=True)

    elif choice == "About":
        about()




if __name__ == "__main__":
    main()