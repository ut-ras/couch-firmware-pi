#!/usr/bin/python

# pip install evdev
# cat /dev/input/event0

from Controllers.Controller import Controller
from evdev import InputDevice, categorize, ecodes, KeyEvent
from threading import Thread
from select import select
import pprint

# See https://stackoverflow.com/questions/19203819/reading-joystick-values-with-python
# and https://theraspberryblonde.wordpress.com/2016/06/29/ps3-joystick-control-with-pygame/
# on how to use pygame to read joystick/gamepad inputs

# Device event library evdev
# https://python-evdev.readthedocs.io/en/latest/tutorial.html

class LogitechGamepad(Controller):
    def __init__(self,name="Logitech Gamepad"):
        super().__init__(name)
        self.gamepad = InputDevice('/dev/input/event0')
        print(self.gamepad)

        #get input options
        print(pprint.pformat(self.gamepad.capabilities(verbose=True)))

        self.joystickMax = 255

    def getStatus(self):
        pass

    def startController(self):
        """
        Starts a thread that continuously reads gamepad and updates Controller variables
        """
        self.updateThread = Thread(target=self.updateLoop(), daemon=True)
        self.updateThread.start()

    def updateLoop(self):
        for event in self.gamepad.read_loop():
            self.handleEvent(event)

    def readAndUpdate(self):
        r,w,x = select([self.gamepad], [], [])
        for event in self.gamepad.read():
            self.handleEvent(event)

    def handleEvent(self, event):
        if event.type == ecodes.EV_KEY:
            keyevent = categorize(event)
            print(keyevent.event)
            print(keyevent.keycode)

            #Buttons example with KeyEvent
            #if keyevent.keystate == KeyEvent.key_down:
            #    if keyevent.keycode[0] == 'BTN_A':
            #        pass
            
        elif event.type == ecodes.EV_ABS:
            absevent = categorize(event)
            print(absevent.event)
            print(absevent.event.value)

            # AbsEvent code values
            #ABS_Y / 1 / Left Y
            #ABS_X / 0 / Left X
            #ABS_RZ / 5 / Right Y
            #ABS_Z / 2 / Right X

            if absevent.event.code == ecodes.ABS_Y:
                #Left Y
                self.leftMotorPercent = (1 - (absevent.event.value / self.joystickMax))
            elif absevent.event.code == ecodes.ABS_RZ:
                #Right Y
                self.rightMotorPercent = (1 - (absevent.event.value / self.joystickMax))
