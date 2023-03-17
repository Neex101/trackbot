'''
Created on 7th March 2023
@author: Ed
This module defines the machine's properties (e.g. travel), services (e.g. serial comms) and functions (e.g. move left)
'''

import serial_connection
import cv_camera

from kivy.clock import Clock
import sys, os, time
from datetime import datetime
import os.path
from os import path

import pilot


#from __builtin__ import True


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))


class TrackBotMachine(object):
    
    serial_conn = None # serial object
    cv = None # camera vision
    track_pilot = None # controller used to track objects in cv

    mX, mX_min, mX_max = 0, 0, 180 # machine co-ordinates for X, degrees
    mY, mY_min, mY_max = 0, 0, 180 # machine co-ordinates for Y, degrees
    mZ, mZ_min, mZ_max = 0, -45, 45 # machine co-ordinates for Z, degrees | Z initialises at zero (mid position) and can enter negative space

    def __init__(self, screen_manager, make_serial_connection):

        self.sm = screen_manager

        if make_serial_connection: self.serial_conn = serial_connection.SerialConnection(self, self.sm)
        self.run_initial_setup_with_marlin()
        
        self.cv = cv_camera.CV_Camera(self.sm)
        
        # The pilot is the control mechanism which reads the inputs and tells the machine what to do - so it's the algorithm of how things move.
        self.track_pilot = pilot.Pilot(self.sm, self)

    def __del__(self):
        log('trackbot_machine destructor')

    def run_initial_setup_with_marlin(self):
        log("WARNING!! Overriding steps per Z degree:")
        self.send_to_serial("M92 Z52.22222222") # WARNING!! Overriding steps per Z degree

    # number of degrees to rotate z axis, relative to current position
    def move_z_angle_relative(self, degrees): 
        # add to current position
        target = degrees + self.mZ        
        # respect soft limits
        if target > self.mZ_max: target = self.mZ_max 
        if target < self.mZ_min: target = self.mZ_min
        self.send_to_serial("G0 Z" + str(target))
        self.send_to_serial("M400") # makes sure ok is not isssued by Marlin until move complete

    # called by first kivy screen when safe to assume kivy processing is completed, to ensure correct clock scheduling
    def start_serial_services(self, dt):
        if self.serial_conn:
            self.serial_conn.start_services()       
    
    def send_to_serial(self, msg):
        if self.serial_conn:
            self.serial_conn.add_to_serial_buffer(str(msg))

    def reset_z_to_zero_pos(self):
        self.mZ = 0
        self.send_to_serial("G92 Z" + str(self.base_rotation_starting_degrees)) # sets base rotation position to be midway at powerup
