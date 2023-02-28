#!/usr/bin/python3

import cv2, libcamera

from picamera2 import Picamera2

# Grab images as numpy arrays and leave everything else to OpenCV.

face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
cv2.startWindowThread()

picam2 = Picamera2()

preview_config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480), })
preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
picam2.configure(preview_config)

picam2.start()

while True:
    im = picam2.capture_array()

    grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(grey, 1.1, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0))
        cx=int(x+x+w)//2
        cy=int(y+y+h)//2
        cv2.circle(img,(cx,cy),5,(0,0,255),-1)

    cv2.imshow("Camera", im)
