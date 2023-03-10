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

        Clock.schedule_interval(self.get_face_centre_from_centre_of_frame_in_x, 2)

    def get_face_centre_from_centre_of_frame_in_x(self, dt):

        if self.m:
            pos = self.m.cv.get_face_from_centre_x()
            log("Face centre in x: " + str(pos))
            self.sm.get_screen('basic_screen').update_position_label_text(str(pos))
            self.m.spin_z(pos)

    def __del__(self):
        
        log('pilot destructor')