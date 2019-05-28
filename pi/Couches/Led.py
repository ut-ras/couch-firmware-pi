import RPi.GPIO as GPIO
import board
import neopixel
import time


# Debug LEDS - for the main program
ledGreen = 17
ledBlue = 27
ledRed = 22

def ledInit(pin):  
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

def ledOut(pin, output):
    GPIO.output(pin, output)


# Wrapper for the NeoPixel object - for examples and custom functions
# https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
class LedStrip():
    pixels = None
    num_pixels = 108         #number of LEDs on the strip        108 = 30 + 30 + 24 + 24
    ORDER = neopixel.GRB    #order of colors on the strip
    
    burntorange = (191, 30, 0)      #should be (191, 87, 0) but the green makes it look yellow

    # NEOPIXEL LED STRIP

    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D18, self.num_pixels, pixel_order=self.ORDER)
        self.clear()

    def clear(self):
        self.fill((0, 0, 0))
        self.brightness(0)

    # colors: tuple
    def fill(self, colors):
        self.pixels.fill(colors)

    # b: float [0, 1]
    def brightness(self, b):
        self.pixels.brightness = b

    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos*3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos*3)
            g = 0
            b = int(pos*3)
        else:
            pos -= 170
            r = 0
            g = int(pos*3)
            b = int(255 - pos*3)
        return (r, g, b) if self.ORDER == neopixel.RGB or self.ORDER == neopixel.GRB else (r, g, b, 0)

    def rainbow_cycle(self):
        for i in reversed(range(self.num_pixels)):
            pixel_index = (i * 256 // self.num_pixels)
            self.pixels[i] = self.wheel(pixel_index & 255)
        self.pixels.show()
            
    #burnt orange
    def longhorn(self):
        for i in reversed(range(self.num_pixels)):
            self.pixels[i] = self.burntorange
        self.pixels.show()
    