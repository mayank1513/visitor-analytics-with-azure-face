import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
import io
import argparse
import cv2
import os
from imutils.video import VideoStream
import time
import tkinter as tk
from shutil import rmtree

# set to your own subscription key value
subscription_key = "5a62ec332ef9459d98d29e08354b3f8c"
assert subscription_key
# replace <My Endpoint String> with the string from your endpoint URL
face_api_url = 'https://southeastasia.api.cognitive.microsoft.com/face/v1.0/detect'

# arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-n", "--detect_every",
                help="detect every nth frame", type=int)
ap.add_argument("-nskip", "--skip_first_n",
                help="skip first n frames", type=int)
ap.add_argument("-o", "--output", type=str,
                help="path to optional output video file")
ap.add_argument("-s", "--output_speed", type=float,
                help="fps factor for output file")
args = vars(ap.parse_args())

# initialize models
headers = {'Content-Type': 'application/octet-stream',
           'Ocp-Apim-Subscription-Key': subscription_key}
params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose',
}

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] starting video stream...")
# if the video argument is None, then the code will read from webcam (work in progress)
if args.get("output_speed", None) is None:
    sx = 1
else:
    sx = args['output_speed']

if args.get("detect_every", None) is None:
    n_skip = 1
else:
    n_skip = args['detect_every']

if args.get("skip_first_n", None) is None:
    skip_first_n = 0
else:
    skip_first_n = args['skip_first_n']

if args.get("video", None) is None:
    cap = VideoStream(src=0).start()
    time.sleep(2.0)
    fps = 30
# otherwise, we are reading from a video file
else:
    cap = cv2.VideoCapture(args["video"])
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    if int(major_ver) < 3:
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
        fps = cap.get(cv2.CAP_PROP_FPS)

writer = None

(H, W) = (None, None)
font = cv2.FONT_HERSHEY_SIMPLEX
# loop over the frames from the video stream
person = 0
faceIds = []
f_genders = []
f_ages = []
f_headPose = []
frame_count = 0
try:
    os.mkdir('visitor_images')
except:
    pass

while True:
        # read the next frame from the video stream and resize it
    frame = cap.read()
    frame_count += 1
    # frame = cap.read()
    frame = frame if args.get("video", None) is None else frame[1]
    # if the frame can not be grabbed, then we have reached the end of the video
    if frame is None:
        break
    # if the frame dimensions are None, grab them
    if W is None or H is None or writer is None:
        (H, W) = frame.shape[:2]
        if args.get("output", None) is not None:
            out_file = os.path.splitext(args["output"])[
                0].replace("\\", "") + "_" + str(sx) + "x.avi"
        elif args.get("video", None) is not None:
            out_file = "out" + \
                os.path.splitext(args["video"])[0].replace(
                    "\\", "") + "_" + str(sx) + "x.avi"
        else:
            out_file = "output" + "_" + str(sx) + "x.avi"
        # print(out_file)
        fourcc = cv2.VideoWriter_fourcc(*"DIVX")
        writer = cv2.VideoWriter(out_file, fourcc, fps/sx, (W, H), True)

    if (n_skip == 1 or frame_count % n_skip == 1) and (frame_count == 1 or frame_count > skip_first_n):
        rects = []
        ids = []
        ages = []
        genders = []
        buf = io.BytesIO()
        plt.imsave(buf, frame, format='jpg')
        img_data = buf.getvalue()

        try:
            response = requests.post(face_api_url, params=params,
                                 headers=headers, data=img_data).json()
        except:
            tk.messagebox.showinfo("Error: Couldn't Connect",
                "Error connecting to the API\nCheck your network connection, subscription key and endpoint")
            exit()

        err = None
        try:
            err = response['error']['message']
        except:
            pass

        if(err):
            tk.messagebox.showinfo("Error: Wrong API", err)
            exit()

        for r in response:
            # print(r)
            ids.append(r['faceId'])
            faceIds.append(r['faceId'])
            rect1 = r['faceRectangle']
            rects.append([rect1['left'], rect1['top'], rect1['left'] +
                          rect1['width'], rect1['top'] + rect1['height']])
            attr = r['faceAttributes']
            ages.append(attr['age'])
            f_ages.append(attr['age'])
            genders.append(attr['gender'])
            f_genders.append(1 if attr['gender'] == 'male' else 0)
            f_headPose.append(attr['headPose'])
            sX, eX, sY, eY = rect1['left']-rect1['width']//2, rect1['left'] + rect1['width'] + \
                rect1['width']//2, rect1['top'] - 3*rect1['height']//4, rect1['top'] + \
                rect1['height'] + rect1['height']//2
            sX, eX, sY, eY = sX if sX > 0 else 0, eX if eX < W else W - \
                1, sY if sY > 0 else 0, eY if eY < H else H - 1
            face_img = cv2.resize(frame[sY:eY, sX:eX].copy(
            ), (10*rect1['width'], 10*rect1['height']), interpolation=cv2.INTER_CUBIC)
            overlay_text = "%s, %d" % (attr['gender'], attr['age'])
            cv2.putText(face_img, overlay_text, (rect1['width']//20, 99*rect1['height']//10),
                        font, 0.8, (255, 0, 0), 2, cv2.LINE_4)
            cv2.imwrite('visitor_images/'+r['faceId']+'.jpg', face_img)

    for i in range(len(rects)):
        (startX, startY, endX, endY) = rects[i]
        gender = genders[i]
        age = ages[i]
        cv2.rectangle(frame, (startX, startY),
                      (endX, endY), (155, 255, 0), 2)
        overlay_text = "%s, %d" % (gender, age)
        cv2.putText(frame, overlay_text, (startX, startY),
                        font, 0.8, (255, 0, 0), 2, cv2.LINE_4)

        # overlay_text = "id = %s" % (ids[i])
        # cv2.putText(frame, overlay_text, (startX, startY + 30),
        # font, 0.5, (0, 0, 255), 2, cv2.LINE_4)
    if writer is not None:
        writer.write(frame)
        # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# response = requests.post(face_api_url, params=params,
                        #  headers=headers, data=img_data).json()
headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': subscription_key,
}

params = {}
d = '{"faceIds": ' + json.dumps(faceIds) + '}'
# print(d)
group_api_url = 'https://southeastasia.api.cognitive.microsoft.com/face/v1.0/group'
response = requests.post(group_api_url, params=params,
                         headers=headers, data=d).json()

# print("----------------------------------")
# print(response)

i = 0
for r in response['groups']:
    try:
        os.mkdir('visitor_images/visitor' + str(i+1))
    except: pass
    age, gender, pose, min_pos_ind, j1 = 0, 0, 180, 0, 0
    for i1 in r:
        ind = faceIds.index(i1)
        age = (j1*age + f_ages[ind])/(j1 + 1)
        gender = (j1*gender + f_genders[ind])/(j1 + 1)
        p = 3*abs(f_headPose[ind]['pitch']) + abs(f_headPose[ind]['roll']) + abs(f_headPose[ind]['yaw'])
        if p < pose:
            pose, min_pos_ind = p, ind
        try:
            os.remove('visitor_images/visitor' + str(i+1) + '/' + i1 + '.jpg')
        except:
            pass
        os.rename('visitor_images/' + i1 + '.jpg', 'visitor_images/visitor' + str(i+1) + '/' + i1 + '.jpg')
        j1 += 1
    person_img = cv2.cvtColor(imread('visitor_images/visitor' + str(i+1) + '/' + faceIds[min_pos_ind] + '.jpg'), cv2.COLOR_BGR2RGB)
    (H, W) = person_img.shape[:2]
    cv2.rectangle(person_img, (0, 94*H//100), (W, H), (255, 255, 0), cv2.FILLED)
    overlay_text = "Visitor %d: %s, %d" % (i+1, 'male' if gender>0.5 else 'female', age)
    cv2.putText(person_img, overlay_text, (W//40, 99*H//100), font, 0.8, (255, 0, 0), 2, cv2.LINE_4)
    cv2.imwrite('visitor_images/visitor' + str(i+1) +'.jpg', person_img)
    rmtree('visitor_images/visitor' + str(i+1))
    i += 1
