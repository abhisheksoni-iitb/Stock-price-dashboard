import cv2
import base64
from io import BytesIO
import numpy as np

"""
Function List
1. frame_count
2. download_link
3. get_optimal_font_scale
4. box_params
5. image_with_bbox
"""


def frame_count(file_path):
    cap = cv2.VideoCapture(file_path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # print( length )
    return length

def download_link(file):
    """Generates a link allowing the PIL image to be downloaded
    in:  PIL image
    out: href string
    """
    buffered = BytesIO()
    file.save(buffered, format="JPEG")
    file_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/jpg;base64,{file_str}" download="processed.png">Download File</a>'
    return href

def get_optimal_font_scale(text, width):
    for scale in reversed(range(0, 10, 1)):
        textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
        new_width = textSize[0][0]
    # print(new_width)
        if (new_width <= width):
            return scale/10
    return 1

def box_params(outs,confidence_threshold,width,height):
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
        
    return class_ids, confidences, boxes

def image_with_bbox(boxes, indexes, img,classes,class_ids,confidences,width):
    font = cv2.FONT_HERSHEY_DUPLEX
    colors = np.random.uniform(100, 255, size=(len(classes), 3))

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
            cv2.rectangle(img, (x, y- int(h/20)), (x + int(w),y + int(h/20)), color, -1)

            # Add text
            fontscale = get_optimal_font_scale(label, width)
            cv2.putText(img, label, (x ,y), font,  fontscale+0.1, (0,0,0),lineType=cv2.LINE_AA)
    return img


if __name__ == "__main__":
    print(frame_count("./123.mp4"))