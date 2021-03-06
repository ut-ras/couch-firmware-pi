# Test main functions for the couch
# To run:
# sudo apt-get install python3-pip
# sudo pip3 install -r requirements.txt
# sudo python3 driveTest.py

# To run python file in background at startup with log files:
# sudo vim /etc/rc.local
#       sudo python3 /home/pi/couch-pi/pi/driveTest.py > /home/pi/couch-pi/pi/logs/log.$(date "+%Y.%m.%d-%H.%M.%S").txt 2>&1 &
#       exit 0

# Enable UART
# add "enable_uart=1" to /boot/config.txt

from time import sleep
import sys


#from Controllers.CommandLineController import CommandLineController
from Controllers.bluetoothController import BluetoothControl
from Controllers.LogitechGamepad import LogitechGamepad
from Couches.testBenchCouch import testBenchCouch
from Drivetrains.OneControllerDrivetrain import OneControllerDrivetrain
import Drivers.Led as Led
from Drivers.Sabertooth import Sabertooth


MAXSPEED = 90        # maxSpeed [0, 100]

def driveTestGamepad():
    Led.ledInit(Led.ledGreen)
    Led.ledInit(Led.ledBlue)
    Led.ledInit(Led.ledRed)

    Led.ledOut(Led.ledBlue, True)

    controller = LogitechGamepad(maxSpeed = MAXSPEED)
    couch = testBenchCouch(controller)

    controller.btnAEvent = couch.toggleLedStrip
    controller.btnXEvent = couch.toggleLedOrange

    if couch.drivetrain.error or controller.error:
        Led.ledOut(Led.ledRed, True)
        sys.exit()

    Led.ledOut(Led.ledGreen, True)

    #couch.startDrivetrainControl(controller_thread=True)
    couch.startDrivetrainControl()
    while True:
        sleep(10)


def driveTestBluetooth():
    Led.ledInit(Led.ledGreen)
    Led.ledInit(Led.ledBlue)
    Led.ledInit(Led.ledRed)

    Led.ledOut(Led.ledBlue, True)

    controller = BluetoothControl()
    couch = testBenchCouch(controller)

    if controller.error:
        Led.ledOut(Led.ledRed, True)
        sys.exit()

    Led.ledOut(Led.ledGreen, True)

    couch.startDrivetrainControl()
    while 1:
       print(controller.getMotorPercents())
       print("-----------")
       sleep(0.2)


def driveTestSabertooth():
    #mC = Sabertooth('/dev/ttyS0')
    #mC.drive(1,80)
    d = OneControllerDrivetrain('/dev/ttyS0')
    d.setSpeed((50, 50))
    while True:
        d.setSpeed((50, 50))
        sleep(1)


#driveTestSabertooth()
driveTestBluetooth()
#driveTestGamepad()
