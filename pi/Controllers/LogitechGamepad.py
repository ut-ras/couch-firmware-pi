#!/usr/bin/python

# pip install evdev
# cat /dev/input/event0

from Controllers.Controller import Controller
from evdev import InputDevice, categorize, ecodes, KeyEvent
from threading import Thread, Timer
from select import select
import pprint
import serial
import time

# See https://stackoverflow.com/questions/19203819/reading-joystick-values-with-python
# and https://theraspberryblonde.wordpress.com/2016/06/29/ps3-joystick-control-with-pygame/
# on how to use pygame to read joystick/gamepad inputs

# Device event library evdev
# https://python-evdev.readthedocs.io/en/latest/tutorial.html

class LogitechGamepad(Controller):
    joystickMax = 255
    leftMotorSetpoint = 0          #percent
    rightMotorSetpoint = 0         #percent

    stopDecelerationTime = 0.5     #seconds - for stop, decelerate from maxSpeed to 0 in this amount of time
    stopFast = False
    stopJoystickThresh = 5         #trigger fast stop when both joysticks under this value
    
    acceleration = 30              #percent per second - general acceleration/deceleration
    accelerationUpdateTime = 0.1   #seconds

    toggleLeftBump = False
    toggleRightBump = False
    toggleA = False
    toggleX = False
    toggleB = False
    btnAEvent = None
    btnXEvent = None

    def __init__(self,name="Logitech Gamepad", maxSpeed=100):
        super().__init__(name, maxSpeed)
        try:
            self.gamepad = InputDevice('/dev/input/event0')
            print(self.gamepad)
            print(pprint.pformat(self.gamepad.capabilities(verbose=True))) #get input options
            self.error = False
            Timer(self.accelerationUpdateTime, self.accelerationTimer).start()
        except (FileNotFoundError, serial.SerialException):
            self.gamepad = None
            self.error = True
            print("ERROR Gamepad is not plugged in")            

    def getStatus(self):
        pass

    def accelerationTimer(self):
        startT = time.time()
        leftDiff = self.leftMotorSetpoint - self.leftMotorPercent
        rightDiff = self.rightMotorSetpoint - self.rightMotorPercent
        leftInc = 0
        rightInc = 0

        if abs(self.leftMotorSetpoint) < self.stopJoystickThresh and abs(self.rightMotorSetpoint) < self.stopJoystickThresh:
            leftInc = self.maxSpeed / (self.stopDecelerationTime / self.accelerationUpdateTime) 
            rightInc = self.maxSpeed / (self.stopDecelerationTime / self.accelerationUpdateTime)           
        else:
            leftInc = self.acceleration * self.accelerationUpdateTime
            rightInc = self.acceleration * self.accelerationUpdateTime   
            
        self.leftMotorPercent += min(leftInc, abs(leftDiff)) * (1 if leftDiff > 0 else -1)  
        self.rightMotorPercent += min(rightInc, abs(rightDiff)) * (1 if rightDiff > 0 else -1)  
        waitT = self.accelerationUpdateTime - (time.time() - startT)
        #print("Wait: " + str(waitT))
        Timer(waitT, self.accelerationTimer).start()

    def startController(self):
        """
        Starts a thread that continuously reads gamepad and updates Controller variables
        """
        self.updateThread = Thread(target=self.updateLoop(), daemon=True)
        self.updateThread.start()

    def updateLoop(self):
        if self.gamepad is not None:
            try:
                for event in self.gamepad.read_loop():
                    self.handleEvent(event)
            except Exception as e:
                self.error = True
                print(e)
        else:
            print("ERROR Gamepad is not plugged in")

    def readAndUpdate(self):
        if self.gamepad is not None:
            r,w,x = select([self.gamepad], [], [])
            for event in self.gamepad.read():
                self.handleEvent(event)
        else:
            print("ERROR Gamepad is not plugged in")

    def handleEvent(self, event):
        if event.type == ecodes.EV_KEY:
            keyevent = categorize(event)
            #print(keyevent.event)
            print(keyevent.keycode)

            #Buttons with KeyEvent
            if keyevent.keystate == KeyEvent.key_down:
                if keyevent.keycode == 'BTN_THUMB':
                    self.toggleA = not self.toggleA
                    if self.btnAEvent is not None:
                        Thread(target=self.btnAEvent, name='Btn A Thread', args=(self.toggleA,)).start()
                if keyevent.keycode[0] == 'BTN_JOYSTICK':
                    self.toggleX = not self.toggleX
                    if self.btnXEvent is not None:
                        Thread(target=self.btnXEvent, name='Btn X Thread', args=(self.toggleX,)).start()
                elif keyevent.keycode == 'BTN_THUMB2':
                    self.toggleB = True
                elif keyevent.keycode == 'BTN_BASE':
                    self.toggleLeftBump = True
                elif keyevent.keycode == 'BTN_BASE2':
                    self.toggleRightBump = True
                
                    
            if keyevent.keystate == KeyEvent.key_up:
                if keyevent.keycode == 'BTN_BASE':
                    self.toggleLeftBump = False
                elif keyevent.keycode == 'BTN_BASE2':
                    self.toggleRightBump = False
                elif keyevent.keycode == 'BTN_THUMB2':
                    self.toggleB = False

        elif event.type == ecodes.EV_ABS:
            absevent = categorize(event)
            #print(absevent.event)
            print(str(absevent.event.code) + " " + str(absevent.event.value))

            # AbsEvent code values
            #ABS_Y / 1 / Left Y
            #ABS_X / 0 / Left X
            #ABS_RZ / 5 / Right Y
            #ABS_Z / 2 / Right X

            
            if self.stopFast:
                self.leftMotorSetpoint = 0
                self.rightMotorSetpoint = 0
            else:
                if absevent.event.code == ecodes.ABS_Y:
                    #Left Y
                    #self.leftMotorPercent = (self.maxSpeed - (2 * self.maxSpeed * absevent.event.value / self.joystickMax))
                    self.leftMotorSetpoint = (self.maxSpeed - (2 * self.maxSpeed * absevent.event.value / self.joystickMax))
                elif absevent.event.code == ecodes.ABS_RZ:
                    #Right Y
                    #self.rightMotorPercent = (self.maxSpeed - (2 * self.maxSpeed * absevent.event.value / self.joystickMax))
                    self.rightMotorSetpoint = (self.maxSpeed - (2 * self.maxSpeed * absevent.event.value / self.joystickMax))

        if self.toggleLeftBump or self.toggleRightBump or self.toggleB:
            self.leftMotorSetpoint = 0
            self.rightMotorSetpoint = 0
            self.stopFast = True
        else:
            self.stopFast = False