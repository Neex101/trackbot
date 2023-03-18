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
    delay_between_tracking_moves = 0.5 # seconds, basic mode
    tracking_clock = None
    is_move_allowed = True # if bot is moving, this flag blocks more move commands from being sent

    z_deadband = 3 # number of degrees movement must exceed before bot moves (to avoid high frequence micromove jitter)
    ser_ok_count = 0


    def __init__(self, screen_manager, machine):
        self.sm = screen_manager
        self.m = machine

    def __del__(self):
        log('pilot destructor')

    def start_tracking(self):
        log("Tracking ON")
        self.is_tracking = True # for button toggle
        self.ser_ok_count = 0
        self.tracking_clock = Clock.schedule_interval(self.spin_z_to_center_the_face, self.delay_between_tracking_moves)

    def stop_tracking(self):
        log("Tracking OFF")
        self.is_tracking = False # for button toggle
        Clock.unschedule(self.tracking_clock)

    def spin_z_to_center_the_face(self, dt):
        if self.m: 
            
            angle = self.m.cv.get_horizontal_degrees_of_face_from_centre()
            self.sm.get_screen('basic_screen').update_position_label_text(str(angle) + " °")

            if self.is_move_allowed and abs(angle) >= self.z_deadband: # # flag blocks move command if moving already & avoids micro-move jitter

                log("Face away from vertical-centre: " + str(angle) + " °")
                self.is_move_allowed = False # blocks any more move requests until scanner receives ok and flips flag again
                self.ser_ok_count = 0

                self.m.move_z_angle_relative(angle)
                self.m.get_ok_when_last_move_complete()

    # serial connection received an 'ok'
    def ser_ok_received(self): 
        self.ser_ok_count += 1
        if self.ser_ok_count == 2: # i.e. ser has recd an ok for the move command, and an ok for the completion
            self.is_move_allowed = True
