#From https://github.com/MomsFriendlyRobotCompany/pysabertooth
##
# Sabertooth.py: Class implementing packetized serial control of
#                Sabertooth 2x32 motor driver (Dimension Engineering).
#
# This code was adapted from MIT licensed
# Copyright 2015, Egan McComb
# copywrite 2017 Kevin J. Walchko
#
##

## CHANGES
# Line 142         the serial flush() command was taking >0.1 seconds, causing some bottleneck and delay, so I removed it

from __future__ import division
import serial
import logging
import time


class Sabertooth(object):
    """
    Sabertooth: A class to control a Sabertooth 2x60 using the packetized
                serial mode (DIP switches 1,2 low).
    https://www.dimensionengineering.com/datasheets/Sabertooth2x60.pdf
    """
    FORWARD_1 = 0x00
    REVERSE_1 = 0x01
    FORWARD_2 = 0x04
    REVERSE_2 = 0x05
    FORWARD_MIXED = 0x08
    REVERSE_MIXED = 0x09
    RIGHT_MIXED = 0x0A
    LEFT_MIXED = 0x0B
    RAMP = 0x10

    serialObject = None

    def __init__(self, address=128):
        """
        baudrate - 2400, 9600, 19200, 38400, 115200
        address - motor controller address
        timeout - serial read time out
        """
        self.address = address

        if 128 > self.address > 135:
            raise Exception('PySabertooth, invalid address: {}'.format(address))


    @classmethod
    def createSerial(cls, port, baudrate=9600, timeout=0.1):
        cls.serialObject = serial.Serial()
        cls.serialObject.baudrate = baudrate
        cls.serialObject.port = port
        cls.serialObject.timeout = timeout

    def __del__(self):
        """
        Destructor, stops motors and closes serial port
        """
        self.stop()
        self.close()
        return

    def info(self):
        """
        Prints out connection info
        """
        print('')
        print('=' * 40)
        print('Sabertooth Motor Controller')
        print('  port: {}'.format(self.serialObject.port))
        print('  baudrate: {}  bps'.format(self.serialObject.baudrate))
        print('  address: {}'.format(self.address))
        print('-' * 40)
        print('')

    @classmethod
    def close(cls):
        """
        Closes serial port
        """
        cls.serialObject.close()

    def setBaudrate(self, baudrate):
        """
        Sets the baudrate to: 2400, 9600, 19200, 38400, 115200
        """
        valid = {
            2400: 1,
            9600: 2,
            19200: 3,
            38400: 4,
            115200: 5
        }

        if baudrate in valid:
            baud = valid[baudrate]
        else:
            raise Exception('PySabertooth, invalid baudrate {}'.format(baudrate))

        # command = 15
        # checksum = (self.address + command + baudrate) & 127
        self.sendCommand(15, baud)
        self.serialObject.write(b'\xaa')
        time.sleep(0.2)

    @classmethod
    def open(cls):
        """
        Opens serial port
        """
        if not cls.serialObject.is_open:
            cls.serialObject.open()
            cls.serialObject.write(b'\xaa')
            cls.serialObject.write(b'\xaa')
        time.sleep(0.2)

    def sendCommand(self, command, message):
        """
        sendCommand: Sends a packetized serial command to the Sabertooth
            command: Command to send.
                FORWARD_1 = 0x00
                REVERSE_1 = 0x01
                FORWARD_2 = 0x04
                REVERSE_2 = 0x05
                FORWARD_MIXED = 0x08
                REVERSE_MIXED = 0x09
                RIGHT_MIXED = 0x0A
                LEFT_MIXED = 0x0B
                RAMP = 0x10
            message: Command
        """
        # Calculate checksum termination (page 23 of the documentation).
        checksum = (self.address + command + message) & 127
        # Write data packet.
        msg = [self.address, command, message, checksum]
        msg = bytes(bytearray(msg))
        self.serialObject.write(msg)
        # Flush UART.
        #self.serialObject.flush()              # the serial flush() command was taking >0.1 seconds, causing some bottleneck and delay, so I removed it

    def stop(self):
        """
        Stops both motors
        """
        sentBytes = 0
        self.driveBoth(0, 0)
        return sentBytes

    def drive(self, motorNum, speed):
        """Drive 1 or 2 motor"""
        # reverse commands are equal to forward+1
        cmds = [self.FORWARD_1, self.FORWARD_2]

        try:
            cmd = cmds[motorNum - 1]
        except:
            raise Exception('PySabertooth, invalid motor number: {}'.format(motorNum))

        if speed < 0:
            speed = -speed
            cmd += 1

        if speed > 100:
            raise Exception('PySabertooth, invalid speed: {}'.format(speed))

        self.sendCommand(cmd, int(127 * speed / 100))

    def driveBoth(self, speed1, speed2):
        """Drive both 1 and 2 motors at once"""
        self.drive(1, speed1)
        self.drive(2, speed2)

    def driveBothSame(self, speed):
        self.driveBoth(speed,speed)

    @classmethod
    def text(cls, cmds):
        """Send the simple ASCII commands"""
        cls.serialObject.write(cmds + b'\r\n')

    @classmethod
    def textGet(cls, cmds):
        """Send the simple ASCII commands"""
        cls.text(cmds)
        ans = cls.serialObject.read(100)
        return ans
