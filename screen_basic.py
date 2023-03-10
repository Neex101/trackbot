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



""")


class BasicDevScreen(Screen):

    screen_manager = ObjectProperty()
    machine = ObjectProperty()

    def __init__(self, **kwargs):
        
        super(BasicDevScreen, self).__init__(**kwargs)
        self.sm=kwargs['screen_manager']
        self.m=kwargs['machine']

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
