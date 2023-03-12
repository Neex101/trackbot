# -*- coding: utf-8 -*-
'''
Created March 2023
@author: Ed
Basic dev screen
'''

import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import sys, os
from kivy.clock import Clock
from datetime import datetime
from kivy.properties import ObjectProperty


Builder.load_string("""

<BasicDevScreen>:

    cool_down_label : cool_down_label
    gCodeInput:gCodeInput
    enter_button: enter_button


    BoxLayout: 
        spacing: 0
        padding: 20
        orientation: 'vertical'
        size_hint: (None, None)
        height: 480
        width: 800
        canvas:
            # Color: 
            #     rgba: hex('#E5E5E5FF')
            Rectangle: 
                size: self.size
                pos: self.pos         

        BoxLayout: 
            spacing: 0
            padding: 
            orientation: 'vertical'
            canvas:
                Color: 
                    rgba: [1,1,1,1]
                RoundedRectangle:
                    size: self.size
                    pos: self.pos    
            
            Label:
                id: cool_down_label
                size_hint_y: 1
                # text: 'Cooling down spindle...'
                color: [0,0,0,1]
                markup: True
                font_size: '30px' 
                valign: 'middle'
                halign: 'center'
                size:self.texture_size
                text_size: self.size

            TextInput:                      
                id:gCodeInput
                multiline: False
                text: ''

            Button:
                id: enter_button
                text: "Enter"
                on_press: root.send_gcode_textinput()
                size_hint_x:0.3
                background_color: .6, 1, 0.6, 1

            Button:
                id: enter_button
                text: "Say something"
                on_press: root.generate_speech()
                size_hint_x:0.3
                background_color: .6, 1, 0.6, 1
""")

def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))


class BasicDevScreen(Screen):

    screen_manager = ObjectProperty()
    machine = ObjectProperty()
    pilot = ObjectProperty()


    def __init__(self, **kwargs):
        
        super(BasicDevScreen, self).__init__(**kwargs)
        self.sm=kwargs['screen_manager']
        self.m=kwargs['machine']
        self.p=kwargs['pilot']
        
        self.cool_down_label.text = 'Test'

    def on_pre_enter(self):
        pass

    def on_enter(self):
        pass    

    def exit_screen(self, dt):
        pass

    def on_leave(self):
        pass

    def update_position_label_text(self, pos):
        self.cool_down_label.text = str(pos)

    def send_gcode_textinput(self): 
        self.m.send_to_serial(str(self.gCodeInput.text))

    def generate_speech(self):

        import threading
        text = "Hello, my name is TrackBot. Or you can call me Three, if you like. I'm pretty dumb right now, but they're giving me upgrades soon which I'm quite excited about. Then maybe I'll do stuff. Until then, saying this sentence is all I can do. And this one. And this one too. And this one. And... ok you get it. Bye bye, for now."
        threading.Thread(target=self.say, args=(text,)).start()

    def say(self, text):

        import pyttsx3
        engine = pyttsx3.init()
        
        log("Saying: " + text)
        engine.say(text)
        engine.runAndWait()
