#!/usr/bin/python3

'''
Created on 7th March 2023
@author: Ed
TrackBotUI
'''

import time
import sys, os
from datetime import datetime
import os.path
from os import path

from kivy.config import Config
from kivy.clock import Clock
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'maxfps', '60')
Config.set('kivy', 'KIVY_CLOCK', 'interrupt')
Config.write()

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window

import trackbot_machine
import pilot

# Screens
import screen_basic

def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))

class TrackBotUI(App):

    def build(self):

        # should serial connection be made? Saves time in dev to not make connection sometimes.
        is_make_serial_connection = None
        if sys.platform == "win32": is_make_serial_connection = False # my dev environment is Windows
        else: is_make_serial_connection = True # TrackBot's OS is Linux

        log("Starting App.")

        # Screens manager object. This will be passed to objects so that they can influence the screens.
        sm = ScreenManager(transition=NoTransition())

        # Physical representation of the robot. It contains movement commands, and it's own camera and serial objects.           
        m = trackbot_machine.TrackBotMachine(sm, is_make_serial_connection)

        # The pilot is the control mechanism which reads the inputs and tells the machine what to do - so it's the algorithm of how things move.
        p = pilot.Pilot(sm, m)

        # Declare screens:
        basic_screen = screen_basic.BasicDevScreen(name='basic_screen', screen_manager = sm, machine = m, pilot = p)

        # Add the screens to screen manager:
        sm.add_widget(basic_screen)

        return sm


if __name__ == '__main__':
    TrackBotUI().run()

