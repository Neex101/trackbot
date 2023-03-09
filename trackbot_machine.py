'''
Created on 7th March 2023
@author: Ed
This module defines the machine's properties (e.g. travel), services (e.g. serial comms) and functions (e.g. move left)
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


class TrackBotMachine(object):

# SETUP
    
    s = None # serial object

    def __init__(self, screen_manager):

        self.sm = screen_manager

        # Establish 's'erial comms and initialise
        self.s = serial_connection.SerialConnection(self, self.sm)
        self.s.find_and_connect_with_trackbot()
