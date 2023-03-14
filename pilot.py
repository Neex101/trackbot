'''
Created on 7th March 2023
@author: Ed
This module controls trackbot's motion requests
'''

import serial_connection
import cv_camera

from kivy.clock import Clock
import sys, os, time
from datetime import datetime
import os.path
from os import path

#from __builtin__ import True


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))


class Pilot(object):
    
    def __init__(self, screen_manager, machine):

        self.sm = screen_manager
        self.m = machine

        # Clock.schedule_interval(self.spin_z_to_center_the_face, 0.2)

    def spin_z_to_center_the_face(self, dt):

        if self.m:
            angle = self.m.cv.get_horizontal_degrees_of_face_from_centre()
            log("Face centre in x: " + str(angle) + "°")
            self.sm.get_screen('basic_screen').update_position_label_text(str(angle))
            self.m.spin_z(angle)

    def __del__(self):
        
        log('pilot destructor')