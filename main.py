#!/usr/bin/python3

'''
Created on 7th March 2023
@author: Ed
TrackBotUI
'''

import time
import sys, os
from datetime import datetime
import os.path
from os import path

from kivy.config import Config
from kivy.clock import Clock
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'maxfps', '60')
Config.set('kivy', 'KIVY_CLOCK', 'interrupt')
Config.write()

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window

import trackbot_machine


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))


class TrackBotUI(App):

    def build(self):

        log("Starting App:")

        # Establish screens
        sm = ScreenManager(transition=NoTransition())

        # Initialise 'm'achine object
        m = trackbot_machine.TrackBotMachine(sm)

        # # initialise the screens (legacy)
        # lobby_screen = screen_lobby.LobbyScreen(name='lobby', screen_manager = sm, machine = m, app_manager = am, localization = l)

        # # add the screens to screen manager
        # sm.add_widget(lobby_screen)

        # return sm


if __name__ == '__main__':
    TrackBotUI().run()




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

while True:
    img = picam2.capture_array()

    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(grey, 1.1, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))
        cx=int(x+x+w)//2
        cy=int(y+y+h)//2
        cv2.circle(img,(cx,cy),5,(0,0,255),-1)

    cv2.imshow("Camera", img)


