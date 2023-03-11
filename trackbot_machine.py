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

#from __builtin__ import True


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))


class TrackBotMachine(object):
    
    serial_conn = None # serial object
    cv = None # camera vision

    def __init__(self, screen_manager, make_serial_connection):

        self.sm = screen_manager
        if make_serial_connection: self.serial_conn = serial_connection.SerialConnection(self, self.sm)
        self.cv = cv_camera.CV_Camera(self.sm)

    def __del__(self):
        log('trackbot_machine destructor')

    def spin_z(self, increment):
        pos = increment / 100
        self.send_to_serial("G0 Z" + str(pos))

    def send_to_serial(self, msg):
        if self.serial_conn:
            self.serial_conn.send(str(msg))