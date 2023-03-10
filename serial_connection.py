'''
Created on 7th March 2023
@author: Ed
Module to manage all serial comms between SW client and FW
'''

from kivy.config import Config
#from __builtin__ import True

import serial, sys, time, string, threading, serial.tools.list_ports
from datetime import datetime, timedelta
from os import listdir
from kivy.clock import Clock

import re
from functools import partial
from serial.serialutil import SerialException


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))


class SerialConnection(object):

    s = None    # Serial comms object
    sm = None   # Screen manager object
    
    # Serial connection details
    BAUD_RATE = 115200 

    def __init__(self, machine, screen_manager):
        
        self.m = machine
        self.sm = screen_manager

        self.find_and_connect_with_trackbot()


    def __del__(self):
        if self.s: self.s.close()
        log('Serial connection destructor')

    # Primary fuunction to establish serial connection
    def find_and_connect_with_trackbot(self):

        log('Attempt serial connection...')
        trackbot_port = ''

        # if Windows, for dev
        if sys.platform == "win32":

            # Gather list of all serial com ports
            port_list = [port.device for port in serial.tools.list_ports.comports() if 'n/a' not in port.description]
            port_list.reverse() # just quicker order sometimes

            log("Windows port list: " + str(port_list)) # for debugging

            for comport in port_list:
                log("Trying port: " + comport)            
                trackbot_port = self.is_port_actually_a_trackbot(comport)
                if trackbot_port: break

        # If Linux
        else:
            # list of portst that we may want to use, in order of preference
            default_serial_port = 'ttyS'
            ACM_port = 'ttyACM'
            USB_port = 'ttyUSB'
            AMA_port = 'ttyAMA'

            port_list = [default_serial_port, ACM_port, USB_port, AMA_port]
            filesForDevice = listdir('/dev/') # put all device files into list[]
            list_of_available_ports = [port for potential_port in port_list for port in filesForDevice if potential_port in port] # this comes out in order of preference too :)
            log("Linux port list: " + str(list_of_available_ports))

            # set up serial connection with first (most preferred) available port
            for available_port in list_of_available_ports:
                log("Trying port: " + available_port)            
                trackbot_port = self.is_port_actually_a_trackbot('/dev/' + str(available_port))
                if trackbot_port: break

        # Display result         
        if self.is_connected():
            log("Serial connection made to TrackBot, on port:" + str(trackbot_port) + ". It's go time.")
        else:
            log("Serial connection not made.")


    def is_port_actually_a_trackbot(self, available_port):

        # Expected send/receive data
        ping_message = b"M115\n"
        expected_response_key = "FIRMWARE_NAME:Marlin"
        
        try: 
            # set up connection
            self.s = serial.Serial(str(available_port), self.BAUD_RATE, timeout = 1, writeTimeout = 1) # assign

            try:
                self.s.flushInput()
                log("Pinging...")
                self.s.write(ping_message)

                first_line = self.s.readline()
                log("Pinged:" + str(available_port) + " | Response: " + str(first_line))

                if first_line:

                    if expected_response_key in str(first_line):

                        log("Expected response :-)")
                        self.s.flushInput()
                        return available_port

                    else:
                        
                        log("Response not recognised")
                        self.s.close()
                else:
                    self.s.close()
                    log("Nothing in the read buffer")

            except:
                log("Serial connection made, but unable to detect Trackbot")
                self.s.close()

        except: 
            log("No serial connection was possible")

        return ''

    # is serial port connected?
    def is_connected(self):

        # if self.s != None and self.s.isOpen():
        if self.s.isOpen():
            return True
        else: 
            return False

    # write something to the serial port
    def send(self, message):
        if self.s.isOpen():
            payload = message + "\n" 
            self.s.write(payload)
