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
    
    is_tracking = False # initlal tracking status
    delay_between_tracking_updates = 3 # seconds, basic mode
    tracking_clock = None

    def __init__(self, screen_manager, machine):

        self.sm = screen_manager
        self.m = machine

    def start_tracking(self):
        log("Tracking ON")
        self.is_tracking = True
        self.tracking_clock = Clock.schedule_interval(self.spin_z_to_center_the_face, self.delay_between_tracking_updates)
    
    def stop_tracking(self):
        log("Tracking OFF")
        self.is_tracking = False
        Clock.unschedule(self.tracking_clock)    

    def spin_z_to_center_the_face(self, dt):

        if self.m:
            angle = self.m.cv.get_horizontal_degrees_of_face_from_centre()
            log("Face away from vertical-centre: " + str(angle) + "°")
            self.sm.get_screen('basic_screen').update_position_label_text(str(angle))
            self.m.move_z_angle_relative(angle)

    def __del__(self):
        
        log('pilot destructor')