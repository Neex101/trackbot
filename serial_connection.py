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



BAUD_RATE = 115200
ENABLE_STATUS_REPORTS = True
GRBL_SCANNER_MIN_DELAY = 0.01 # Delay between checking for response from grbl. Needs to be hi-freq for quick streaming, e.g. 0.01 = 100Hz


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))


class SerialConnection(object):

    STATUS_INTERVAL = 0.1 # How often to poll general status to update UI (0.04 = 25Hz = smooth animation)

    s = None    # Serial comms object
    sm = None   # Screen manager object

    
    write_command_buffer = []
    write_realtime_buffer = []
    
    # Flag to kill grbl scanner (used in zhead cycle app)
    # Need to disable grbl scanner before closing serial connection, or else causes problems (at least in windows)
    grbl_scanner_running = False

    def __init__(self, machine, screen_manager):

        self.m = machine
        self.sm = screen_manager

    def __del__(self):
        if self.s: self.s.close()
        log('Serial connection destructor')

    # Unused utility function to bypass autodetect port function for debug
    def quick_connect(self, available_port):
        try: 
            log("Try to connect to: " + available_port)
            # set up connection
            self.s = serial.Serial(str(available_port), BAUD_RATE, timeout = 6, writeTimeout = 20) # assign
            self.s.flushInput()
            self.s.write("\x18")
            return available_port
        
        except:
            log("Could not connect to given port.")
            return ''

    # Primary fuunction  to establish connection
    def autodetect_port_and_establish_connection(self):

        log('Start to establish connection...')
        trackbot_port = ''

        # if Windows
        if sys.platform == "win32":

            port_list = [port.device for port in serial.tools.list_ports.comports() if 'n/a' not in port.description]

            print("Windows port list: ") # for debugging
            print(str(port_list))

            for comport in port_list:

                print("Trying Windows port: ")
                print (comport)

                trackbot_port = self.is_port_actually_a_trackbot(comport)
                if trackbot_port: break
                
            if not trackbot_port: 
                log("No arduino connected")

        elif sys.platform == "darwin":
            self.suppress_error_screens = True

            filesForDevice = listdir('/dev/') # put all device files into list[]
            for line in filesForDevice:
                if line.startswith('tty.usbmodem'): # look for... 

                    print("Mac port to try: ") # for debugging
                    print (line)

                    trackbot_port = self.is_port_actually_a_trackbot('/dev/' + str(line))
                    if trackbot_port: break

            if not trackbot_port: 
                log("No arduino connected")

        else:
            try:
                # list of portst that we may want to use, in order of preference
                default_serial_port = 'ttyS'
                ACM_port = 'ttyACM'
                USB_port = 'ttyUSB'
                AMA_port = 'ttyAMA'

                port_list = [default_serial_port, ACM_port, USB_port, AMA_port]

                filesForDevice = listdir('/dev/') # put all device files into list[]

                # this comes out in order of preference too :)
                list_of_available_ports = [port for potential_port in port_list for port in filesForDevice if potential_port in port]

                # set up serial connection with first (most preferred) available port
                for available_port in list_of_available_ports:
                    trackbot_port = self.is_port_actually_a_trackbot('/dev/' + str(available_port))
                    if trackbot_port: break

                # If all else fails, try to connect to ttyS or ttyAMA port anyway
                if trackbot_port == '':

                    first_port = list_of_available_ports[0]
                    last_port = list_of_available_ports[-1]
                    try: 
                        if default_serial_port in first_port:
                            first_list_index = 1
                            self.s = serial.Serial('/dev/' + first_port, BAUD_RATE, timeout = 6, writeTimeout = 20) # assign
                            trackbot_port = ": could not identify if any port was SmartBench, so attempting " + first_port
                    except: 
                        if AMA_port in last_port:
                            last_list_index = -1
                            self.s = serial.Serial('/dev/' + last_port, BAUD_RATE, timeout = 6, writeTimeout = 20) # assign
                            trackbot_port = ": could not identify if any port was SmartBench, so attempting " + last_port

                    if trackbot_port == '':
                        Clock.schedule_once(lambda dt: self.get_serial_screen('Could not establish a connection on startup.'), 5)

            except:
                # I doubt this will be triggered with all the other try-excepts, but will leave it in anyway. 
                Clock.schedule_once(lambda dt: self.get_serial_screen('Could not establish a connection on startup.'), 5) # necessary bc otherwise screens not initialised yet      

        log("Serial connection status: " + str(self.is_connected()) + " " + str(trackbot_port))
        
        try: 
            if self.is_connected():
                log("Go time...")
                # self.write_direct("\r\n\r\n", realtime = False, show_in_sys = False, show_in_console = False)    # Wakes grbl

        except:
            log("Serial connection made, but didn't like first command :-(")      


    def is_port_actually_a_trackbot(self, available_port):

        try: 
            log("Try to connect to: " + available_port)
            # set up connection
            self.s = serial.Serial(str(available_port), BAUD_RATE, timeout = 6, writeTimeout = 20) # assign

            # reopen port, just in case its been in use somewhere else
            self.s.close()
            self.s.open()
            # serial object needs time to make the connection before we can do anything else
            time.sleep(1)

            try:
                # flush input and soft-reset: this will trigger the GRBL welcome message
                self.s.flushInput()
                self.s.write("M115")
                # give it a second to reply
                time.sleep(0.5)
                first_bytes = self.s.inWaiting()
                log("Is port SmartBench? " + str(available_port) + "| First read: " + str(first_bytes))

                if first_bytes:

                    # Read in first input and log it
                    def strip_and_log(input_string):
                        new_string = input_string.strip()
                        log(new_string)
                        return new_string

                    stripped_input = map(strip_and_log, self.s.readlines())

                    # Is this device a SmartBench? 
                    if any('FIRMWARE' in ele for ele in stripped_input):
                        # Found SmartBench! 
                        trackbot_port = available_port

                        log("FOUND PORT!!!!!!!!!!!!!!!!!!!!!!!")

                        return trackbot_port

                    else:
                        self.s.close()
                else:
                    self.s.close()

            except:
                log("Could not communicate with that port at all")

        except: 
            log("Wow definitely not that port")

        return ''

    # is serial port connected?
    def is_connected(self):

        if self.s != None:
            return True
        else: 
            return False

    # called by first kivy screen when safe to assume kivy processing is completed, to ensure correct clock scheduling
    def start_services(self, dt):

        log('Starting services')
        self.s.flushInput()  # Flush startup text in serial input
        self.next_poll_time = time.time()
        self.grbl_scanner_running = True
        t = threading.Thread(target=self.grbl_scanner)
        t.daemon = True
        t.start()
        
        # Clear any hard switch presses that may have happened during boot
        self.m.bootup_sequence()

        self.m.starting_serial_connection = False