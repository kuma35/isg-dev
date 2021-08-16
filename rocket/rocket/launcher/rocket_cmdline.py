#!/usr/bin/env python
# -*- coding:utf-8 -*-

import locale
CONSOLE_ENCODE = locale.getpreferredencoding()
import sys
from time import sleep
from rocket_backend import RocketManager

button_labels = ["Down", "Up", "Left", "Right", "_Fire"]
counter_pan = 0
counter_tilt = 0
CMD_PROMPT = 'command>'

def do_move(launcher, command_index, time) :
    if not launcher.previous_limit_switch_states[command_index] :
        launcher.start_movement(command_index)
        if time :
            sleep(time)
        launcher.stop_movement()
        launcher.check_limits()

def do_down(launcher, time=0.3) :
    do_move(launcher, 0, time)

def do_up(launcher, time=0.3) :
    do_move(launcher, 1, time)

def do_left(launcher, time=0.5) :
    do_move(launcher, 2, time)

def do_right(launcher, time=0.5) :
    do_move(launcher, 3, time)
    pass

def do_fire(launcher) :
    pass

def do_center(launcher) :
    #pan center
    while not launcher.previous_limit_switch_states[2] :
        do_left(launcher)
    count = 0
    while not launcher.previous_limit_switch_states[3] :
        do_right(launcher)
        count += 1
    #print "total count=%d"%(count),
    for i in range(1, count/2) :   # right is unlimitation.... can not check limit switch?
        do_left(launcher)
        #print "left=%d"%(i),
    #for i in range(1, 30/2) :   # right is unlimitation.... can not check limit switch?
    #    do_left(launcher)
    #tilt center
    while not launcher.previous_limit_switch_states[0] :
        do_down(launcher)
    count = 0
    while not launcher.previous_limit_switch_states[1] :
        do_up(launcher)
        count += 1
    for i in range(1, count/2) :
        do_down(launcher)
    #print "center done"
def do_reset(launcher) :
    while not launcher.previous_limit_switch_states[2] :
        do_left(launcher)
    while not launcher.previous_limit_switch_states[0] :
        do_down(launcher)

ctrl = RocketManager()
err_msg = ctrl.acquire_devices()
if err_msg :
    print err_msg
    sys.exit(1)
# メインループ
launcher = ctrl.launchers[0] # :-)
command = ''
while command != 'q' :
    inputStr = raw_input(CMD_PROMPT)
    commands = []
    commands = inputStr.split(' ')
    for command in commands :
        if command == 'q ':
            break
        elif command == 'u':
            do_up(launcher)
        elif command == 'd':
            do_down(launcher)
        elif command == 'l':
            do_left(launcher)
        elif command == 'r':
            do_right(launcher)
        elif command == 'f':
            do_fire(launcher)
        elif command == 'c':
            do_center(launcher)
        elif command == 'reset':
            do_reset(launcher)
        else :
            None
# 後始末
for launcher in ctrl.launchers:
    launcher.stop_movement()

