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

def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))

class TrackBotUI(App):

    def build(self):

        log("Starting App:")

        # Establish screens
        sm = ScreenManager(transition=NoTransition())

        # Initialise 'm'achine object
        m = trackbot_machine.TrackBotMachine(sm)

        # # initialise the screens (legacy)
        # lobby_screen = screen_lobby.LobbyScreen(name='lobby', screen_manager = sm, machine = m, app_manager = am, localization = l)

        # # add the screens to screen manager
        # sm.add_widget(lobby_screen)

        return sm


if __name__ == '__main__':
    TrackBotUI().run()

