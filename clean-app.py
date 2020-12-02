# Importing required libraries
import streamlit as st
import cv2
import numpy as np
import os
import PIL
from PIL import Image
import base64
from io import BytesIO
import pandas as pd
import sqlite3 
############
from funcs import *
from database import *
#############

# Load Yolo
net = cv2.dnn.readNetFromDarknet("model/yolov3.cfg",
                                     "model/yolov3.weights")

classes = []
with open("model/classes.txt", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]


def about():
	st.write('')


def main():
    st.title("Object detection App")
    st.write("")


    activities = ["Home","Login","SignUp", "About"]
    choice = st.sidebar.selectbox("Section", activities)

    # DB Management
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    if choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login"):
            # if password == '12345':
            create_usertable(c)
            hashed_pswd = make_hashes(password)

            result = login_user(username,check_hashes(password,hashed_pswd),c)
            if result:
                st.balloons()
                st.success("Logged In as {}".format(username))

                task = st.selectbox("Task",["Add Post","Profiles"])
                if task == "Add Post":
                    st.subheader("Add Your Post")

                elif task == "Analytics":
                    st.subheader("Analytics")
                elif task == "Profiles":
                    st.subheader("User Profiles")
                    user_result = view_all_users(c)
                    clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
                    st.dataframe(clean_db)
            else:
                st.warning("Incorrect Username/Password")

    
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')

        if st.button("Signup"):
            create_usertable(c)
            add_userdata(new_user,make_hashes(new_password),c,conn)
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")



    elif choice == "Home":
        confidence_threshold = st.sidebar.slider("Confidence threshold", 0.0, 1.0, 0.5, 0.01)                
        # You can specify more file types below if you want
        image_file = st.file_uploader("Upload image", type=['jpeg', 'png', 'jpg', 'webp'])
        processed = False
        if image_file is not None:
            # create_storage(cur)
            if st.button("Process the Video"):

                if processed==False:
                    # st.write(type(image_file))
                    cap = cv2.VideoCapture('123.mp4')
                    cap.set(cv2.CAP_PROP_FPS, 23)

                    # frame_width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    # frame_height =int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))
                    processed_video = "output2.avi"
                    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
                    output = cv2.VideoWriter(processed_video, fourcc, 23.0, (1280,720))

                    
                    success = True
                    image_placeholder = st.empty()
                    my_bar = st.progress(0)
                    total_frames = frame_count("./123.mp4")
                    frame_iter = 0
                    percent_complete =0
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

                            class_ids, confidences, boxes = box_params(outs,confidence_threshold,width,height)

                            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
                            # print(indexes)
                            
                            img = image_with_bbox(boxes, indexes, img,classes,class_ids,confidences,width)
                            img = cv2.resize(img, (1280,720))
                    #         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                            output.write(img)
                            # plt.imshow(img)
                            # plt.show()
                            img_show = cv2.resize(img, (680,480))
                            image_placeholder.image(img_show, channels="RGB")
                            my_bar.progress(int(percent_complete + 1))
                            frame_iter +=1
                            percent_complete = 100*(frame_iter/total_frames)
                            # time.sleep(0.01)
                            # st.image(img, use_column_width = True)  

                
                    cap.release()
                    processed = True

        # if processed:
        if st.button('Create Download Link') and processed:
            result = Image.fromarray(img)
            st.markdown(download_link(result), unsafe_allow_html=True)

    elif choice == "About":
        about()



if __name__ == "__main__":
    main()