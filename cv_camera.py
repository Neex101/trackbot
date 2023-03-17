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

if sys.platform == "linux" or sys.platform == "linux2":
    import cv2, libcamera
    from picamera2 import Picamera2

#from __builtin__ import True


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))

class CV_Camera(object):

    # cam_frame_x_size, cam_frame_y_size, viewing_angle = 640, 480, 90 # rpi cam mod 3 REG
    cam_frame_x_size, cam_frame_y_size, viewing_angle = 768, 432, 74 # rpi cam mod 3 WIDE
    cx, cy = cam_frame_x_size / 2, cam_frame_y_size / 2 # face centres, measured from top left of frame
    
    picam2 = None
    face_detector = None
    horiztonal_pixels_per_degree_of_vision = cam_frame_x_size / viewing_angle

    def __init__(self, screen_manager):

        self.new_face_data = False    

        self.sm = screen_manager

        # if Windows, for dev
        if sys.platform == "win32":
            log("No CV")

        # if Linux
        else:        
            log("Starting CV")


            # Grab images as numpy arrays and leave everything else to OpenCV.
            self.face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
            cv2.startWindowThread()
            self.picam2 = Picamera2()
            # preview_config = self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (self.cam_frame_x_size, self.cam_frame_y_size), })
            # preview_config = self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080), })
            preview_config = self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (768, 432), })
            preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
            self.picam2.configure(preview_config)
            self.picam2.start()
            log("Camera started.")

            Clock.schedule_interval(self.capture_and_detect, 0.2)

    def capture_and_detect(self, dt):

        self.new_face_data = False    
        img = self.picam2.capture_array()

        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(grey, 1.1, 5)

        for (x, y, w, h) in faces:

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))
            self.cx=int(x+x+w)//2
            self.cy=int(y+y+h)//2
            cv2.circle(img,(self.cx,self.cy),5,(0,0,255),-1)
            self.new_face_data = True    

        cv2.imshow("Camera", img)


    def get_face_from_centre_x(self):
        
        # cx & cy work from top left of frame
        x_coord_from_center = self.cx - self.cam_frame_x_size/2

        return x_coord_from_center
        

    def get_horizontal_degrees_of_face_from_centre(self):
        
        if self.new_face_data:    
            x_pixels_from_center = self.cx - self.cam_frame_x_size/2
            degrees_from_center = round((x_pixels_from_center / self.horiztonal_pixels_per_degree_of_vision), 3)
            return degrees_from_center
        else:
            return 0

