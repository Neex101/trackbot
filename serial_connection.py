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
    STATUS_INTERVAL = 1  # How often to poll general status to update UI (0.04 = 25Hz = smooth animation)
    poll_for_status = False

    def __init__(self, machine, screen_manager):
        
        self.m = machine
        self.sm = screen_manager
        self.find_and_connect_with_trackbot()
        # self.start_services() is not called here, it is called by last kivy screen to load, to ensure that all Clock schedules run as expected

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

    write_to_serial_buffer = []

    # add something to the queue for something to get sent
    def add_to_serial_buffer(self, message):
        payload = message
        self.write_to_serial_buffer.append(payload)

    # Never access this directly, instead, add_to_serial_buffer. 
    # This fn is what actually writes to the serial connectipn, and should only ever be called by the scanner.
    # This makes sure we don't loose anything between threads.
    def _write_to_serial(self, message):
        if self.s.isOpen():
            log(" >>> " + str(message))
            self.s.write(str.encode(str(message + "\n")))

    # called by first kivy screen when safe to assume kivy processing is completed, to ensure correct clock scheduling
    def start_services(self):

        log('Starting serial connection services')
        self.s.flushInput()  # Flush startup text in serial input
        self.next_poll_time = time.time() # means will poll asap
        t = threading.Thread(target=self.serial_scanner_loop)
        t.daemon = True
        self.FLUSH_FLAG = True # flag to clear incoming serial buffer on first loop run
        self.is_serial_scanner_running = True # flag to stop/start loop
        t.start()


    # SCANNER: listens for responses from Grbl
    # "Response" is a message from GRBL saying how a line of gcode went (either 'ok', or 'error') when it was loaded from the serial buffer into the line buffer
    # When streaming, monitoring the response from GRBL is essential for EasyCut to know when to send the next line
    # Full docs: https://github.com/gnea/grbl/wiki/Grbl-v1.1-Interface
    # "Push" is for messages from GRBL to provide more general feedback on what Grbl is doing (e.g. status)

    VERBOSE_ALL_PUSH_MESSAGES = False
    VERBOSE_ALL_RESPONSE = True
    VERBOSE_STATUS = False

    def serial_scanner_loop(self):

        log('Running serial scanner loop on external thread')

        while self.is_serial_scanner_running:

            if self.FLUSH_FLAG == True:
                self.s.flushInput()
                self.FLUSH_FLAG = False

            # Poll for status
            if self.poll_for_status and self.next_poll_time < time.time():
                self._write_to_serial('M114 R')
                self.next_poll_time = time.time() + self.STATUS_INTERVAL

            # Process anything in the write_to_serial_buffer
            command_counter = 0
            for command in self.write_to_serial_buffer:
                self._write_to_serial(command)
                command_counter += 1
            del self.write_to_serial_buffer[0:(command_counter)]

            # If there's a message received, attempt to strip it...
            if self.s.inWaiting():
                # Read line in from serial buffer
                try:
                    rec_temp = self.s.readline().strip()  # Block the executing thread indefinitely until a line arrives
                    rec_temp - rec_temp.decode('ascii')
                except Exception as e:
                    log(' <<< ERROR: serial.readline exception: ' + str(e))
                    rec_temp = ''
            else:
                rec_temp = ''

            # ...if stripped ok, process it. 
            if len(rec_temp):

                if self.VERBOSE_ALL_RESPONSE: log(" <<< " + str(rec_temp))

                if rec_temp == 'ok':
                    if self.m.track_pilot.is_tracking: self.m.track_pilot.is_move_allowed = True
                    
                # # Update the gcode monitor (may not be initialised) and console:
                # try:
                #     self.sm.get_screen('home').gcode_monitor_widget.update_monitor_text_buffer('rec', rec_temp)
                # except:
                #     pass

                # # Process the GRBL response:
                # # NB: Sequential streaming is controlled through process_grbl_response
                # try:
                #     # If RESPONSE message (used in streaming, counting processed gcode lines)
                #     if rec_temp.startswith(('ok', 'error')):
                #         self.process_grbl_response(rec_temp)
                #     # If PUSH message
                #     else:
                #         self.process_grbl_push(rec_temp)

                # except Exception as e:
                #     log('Process response exception:\n' + str(e))
                #     self.get_serial_screen('Could not process grbl response. Grbl scanner has been stopped.')

                # # Job streaming: stuff buffer
                # if (self.is_job_streaming):
                #     if self.is_stream_lines_remaining:
                #         self.stuff_buffer()
                #     else:
                #         if self.g_count == self.l_count:
                #             self.end_stream()
