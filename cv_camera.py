'''
Created on 9th March 2023
@author: Ed
This module defines the machine's CV (computer vision) properties
'''

import serial_connection
from kivy.clock import Clock
import sys, os, time
from datetime import datetime
import os.path
from os import path


#from __builtin__ import True


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))

class CV_Camera(object):

    cx, cy = 0, 0 # face centres
    
    def __init__(self, screen_manager):
        self.sm = screen_manager

        # if Windows, for dev
        if sys.platform == "win32":
            log("No CV")

        # if Linux
        else:        
            log("Starting CV")

            import cv2, libcamera
            from picamera2 import Picamera2
            # Grab images as numpy arrays and leave everything else to OpenCV.
            face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
            cv2.startWindowThread()
            picam2 = Picamera2()
            preview_config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480), })
            # preview_config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080), })
            preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
            picam2.configure(preview_config)
            picam2.start()

            log("Camera started.")

            while True:
                img = picam2.capture_array()

                grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_detector.detectMultiScale(grey, 1.1, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))
                    self.cx=int(x+x+w)//2
                    self.cy=int(y+y+h)//2
                    cv2.circle(img,(self.cx,self.cy),5,(0,0,255),-1)
                    log(str(self.cx,self.cy))


                cv2.imshow("Camera", img)

    def get_face_xy_from_centre():
        return self.cx, self.cy
        


